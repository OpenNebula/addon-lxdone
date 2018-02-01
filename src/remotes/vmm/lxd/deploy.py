#!/usr/bin/python

# -------------------------------------------------------------------------- #
# Copyright 2016-2018                                                        #
#                                                                            #
# Portions copyright OpenNebula Project (OpenNebula.org), CG12 Labs          #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
# -------------------------------------------------------------------------- #

import lxd_common as lc
t0 = lc.time()
from lxd_common import xml_query_list as xql
from lxd_common import xml_query_dict as xqd

client = lc.Client()


def create_profile(xml):
    'create a container profile from OpenNebula VM template'
    dicc = lc.xml_start(xml)
    pre = lc.xml_pre
    profile = {'config': [], 'devices': []}

    # General
    mapped_entries = [lc.map_ram(xql(pre + 'MEMORY', dicc)[0]),
                      lc.map_cpu(xql(pre + 'CPU', dicc)[0]),
                      lc.map_vcpu(xql(pre + 'VCPU', dicc)[0]),
                      lc.map_xml(xml), {'user.hostname': lc.xql('/VM/NAME', dicc)[0]}]

    for x in mapped_entries:
        profile['config'].append(x)

    profile['VM_ID'] = xql('/VM/ID', dicc)[0]
    profile['CONTEXT_DISK_ID'] = xql(pre + 'CONTEXT/DISK_ID', dicc)[0]

    # VNC
    for x in ['PASSWD', 'PORT']:
        profile['VNC_' + x] = xql(pre + 'GRAPHICS/' + x, dicc)[0]

    # Security
    for x in ['privileged', 'nesting']:
        item = '/VM/USER_TEMPLATE/LXD_SECURITY_' + x.swapcase()
        if dicc.get(item):
            profile['config'].append({'security.' + x: xql(item, dicc)[0]})

    # NETWORK_CONFIG
    NIC = xql('NIC/NIC_ID', dicc)  # NIC_NAME?
    if NIC[0]:
        NIC_BRIDGE = xqd('NIC/BRIDGE', NIC, dicc)
        NIC_MAC = xqd('NIC/MAC', NIC, dicc)
        NIC_TARGET = xqd('NIC/TARGET', NIC, dicc)
        for iface in NIC:
            i = str(iface)
            name = 'eth%s' % (iface)
            profile['devices'].append(lc.map_nic(name, NIC_BRIDGE[i], NIC_MAC[i], NIC_TARGET[i]))

    # STORAGE_CONFIG
    profile['DS_ID'] = xql('/VM/HISTORY_RECORDS/HISTORY/DS_ID', dicc)[0]
    profile['DISK_TYPE'] = xql(pre + 'DISK/TYPE', dicc)[0]
    profile['DISK_CLONE'] = xql(pre + 'DISK/CLONE', dicc)[0]
    profile['DISK_SOURCE'] = xql(pre + 'DISK/SOURCE', dicc)[0]

    # extra
    num_hdds = profile['num_hdds'] = len(profile['DISK_TYPE'])
    profile['DISK_TARGET'] = xql('DISK/TARGET', dicc)
    if num_hdds > 1:
        DISK_ID = xql('DISK/DISK_ID', dicc)
        for x in xrange(1, num_hdds):
            source = lc.storage_sysmap(DISK_ID[x], profile['DISK_TYPE'][x], profile['DISK_SOURCE']
                                       [x], profile['VM_ID'], profile['DS_ID'], profile['DISK_CLONE'][x])
            profile['devices'].append(lc.map_disk(profile['DISK_TARGET'][x], source))

    return profile


def apply_profile(profile, container):
    'apply config and devices to container'
    # STORAGE_CONFIG
    VM_ID = profile['VM_ID']
    DS_ID = profile['DS_ID']
    DISK_TYPE = profile['DISK_TYPE']
    DISK_SOURCE = profile['DISK_SOURCE']
    DISK_CLONE = profile['DISK_CLONE']

    root_source = lc.storage_rootfs_mount(VM_ID, DISK_TYPE[0], DS_ID, DISK_SOURCE[0], DISK_CLONE[0])
    profile['config'].append(root_source)

    if profile['CONTEXT_DISK_ID']:
        CONTEXT_DISK_ID = profile['CONTEXT_DISK_ID']
        DS_ID = profile['DS_ID']
        DS_LOCATION = '/var/lib/one/datastores/' + DS_ID + '/' + VM_ID + '/'  # TODO fix hardcoded
        contextiso = lc.isoparser.parse(DS_LOCATION + 'disk.' + CONTEXT_DISK_ID)
        lc.storage_context(container, contextiso)

    # FIXME: duplicated block of code
    for i in profile['config']:
        try:
            container.config.update(i)
            container.save(wait=True)
        except lc.LXDAPIException as lxdapie:
            lc.log_function(i.keys()[0] + ': ' + str(lxdapie), 'e')
            lc.sys.exit(1)

    for i in profile['devices']:
        try:
            container.devices.update(i)
            container.save(wait=True)
        except lc.LXDAPIException as lxdapie:
            lc.log_function(i.keys()[0] + ': ' + str(lxdapie), 'e')
            lc.sys.exit(1)


# INITIALIZE_CONTAINER
profile = create_profile(lc.sys.argv[1])  # xml is passed by opennebula as argument ex. deployment.0
VM_NAME = 'one-' + profile['VM_ID']
init = {'name': VM_NAME, 'source': {'type': 'none'}}
lc.log_function(lc.separator)

try:
    container = client.containers.create(init, wait=True)
except lc.LXDAPIException as lxdapie:  # probably this container already exists
    container = client.containers.get(VM_NAME)
    if container.status == 'Running':
        lc.log_function("A container with the same ID is already running", 'e')
        lc.sys.exit(1)
apply_profile(profile, container)

# BOOT_CONTAINER
try:
    container.start(wait=True)
except lc.LXDAPIException as lxdapie:
    if container.status == 'Running':
        container.stop(wait=True)
    lc.container_wipe(container, profile)
    lc.log_function(lxdapie, 'e')
    lc.sys.exit(1)

lc.vnc_start(profile['VM_ID'], profile['VNC_PORT'], profile['VNC_PASSWD'])
lc.clock(t0)
print VM_NAME
