#!/usr/bin/python

# -------------------------------------------------------------------------- #
# Copyright 2016-2017                                                        #
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
from lxd_common import xml_query_item as xqi
from pylxd.exceptions import LXDAPIException


client = lc.Client()


def create_profile(xml):
    'create a container profile from OpenNebula VM template'
    dicc = lc.xml_start(xml)
    profile = {'config': [], 'devices': []}

    mapped_entries = [lc.map_ram(xqi('MEMORY', dicc)),
                      lc.map_cpu(xqi('CPU', dicc)),
                      lc.map_vcpu(xqi('VCPU', dicc)),
                      lc.map_xml(xml),
                      {'user.hostname': dicc["/VM/NAME"][0]}]

    for x in mapped_entries:
        profile['config'].append(x)

    VM_ID = profile['VM_ID'] = dicc["/VM/ID"][0]
    profile['CONTEXT_DISK_ID'] = xqi('CONTEXT/DISK_ID', dicc)

    # Security
    for x in ["privileged", "nesting"]:
        item = '/VM/USER_TEMPLATE/LXD_SECURITY_' + x.swapcase()
        if dicc.get(item):
            profile['config'].append({'security.' + x: dicc.get(item)[0]})

    # NETWORK_CONFIG
    NIC = xql('NIC/NIC_ID', dicc)
    if NIC[0]:
        NIC_BRIDGE = xqd('NIC/BRIDGE', NIC, dicc)
        NIC_MAC = xqd('NIC/MAC', NIC, dicc)
        NIC_TARGET = xqd('NIC/TARGET', NIC, dicc)
        for iface in NIC:
            i = str(iface)
            name = 'eth%s' % (iface)
            profile['devices'].append(lc.map_nic(name, NIC_BRIDGE[i], NIC_MAC[i], NIC_TARGET[i]))

    # STORAGE_CONFIG
    DS_ID = profile['DS_ID'] = dicc["/VM/HISTORY_RECORDS/HISTORY/DS_ID"][0]
    DISK_TYPE = profile['DISK_TYPE'] = xql('DISK/TYPE', dicc)
    DISK_CLONE = profile['DISK_CLONE'] = xql('DISK/CLONE', dicc)
    DISK_SOURCE = profile['DISK_SOURCE'] = xql('DISK/SOURCE', dicc)

    # extra
    num_hdds = profile['num_hdds'] = len(profile['DISK_TYPE'])
    profile['DISK_TARGET'] = xql('DISK/TARGET', dicc)
    if num_hdds > 1:
        DISK_ID = xql('DISK/DISK_ID', dicc)
        for x in xrange(1, num_hdds):
            source = lc.storage_sysmap(DISK_ID[x], DISK_TYPE[x],
                                       DISK_SOURCE[x], VM_ID, DS_ID, DISK_CLONE[x])
            profile['devices'].append(lc.map_disk(profile['DISK_TARGET'][x], source))

    # dicc (for lc.vnc_start())
    profile['dicc'] = dicc

    return profile


def apply_profile(profile, container):
    'apply config and devices to container'
    # STORAGE_CONFIG
    VM_ID = profile['VM_ID']
    DS_ID = profile['DS_ID']
    DISK_TYPE = profile['DISK_TYPE']
    DISK_SOURCE = profile['DISK_SOURCE']
    DISK_CLONE = profile['DISK_CLONE']
    # rootfs
    root_source = lc.storage_rootfs_mount(VM_ID, DISK_TYPE[0], DS_ID, DISK_SOURCE[0], DISK_CLONE[0])
    profile['config'].append(root_source)

    if profile['CONTEXT_DISK_ID']:
        CONTEXT_DISK_ID = profile['CONTEXT_DISK_ID']
        DS_ID = profile['DS_ID']
        DS_LOCATION = '/var/lib/one/datastores/' + DS_ID + '/' + VM_ID + '/'
        # push context files into the container
        contextiso = lc.isoparser.parse(DS_LOCATION + 'disk.' + CONTEXT_DISK_ID)
        lc.storage_context(container, contextiso)

    # FIXME: duplicated block of code
    for i in profile['config']:
        try:
            container.config.update(i)
            container.save(wait=True)
        except LXDAPIException as lxdapie:
            lc.log_function('ERROR', 'container: ' + i.keys()[0] + ': ' + str(lxdapie))
            lc.sys.exit(1)

    for i in profile['devices']:
        try:
            container.devices.update(i)
            container.save(wait=True)
        except LXDAPIException as lxdapie:
            lc.log_function('ERROR', 'container: ' + i.keys()[0] + ': ' + str(lxdapie))
            lc.sys.exit(1)


# READ_XML
profile = create_profile(lc.sys.argv[1]) # xml is passed by opennebula as argument ex. deployment.0

VM_ID = profile['VM_ID']
VM_NAME = 'one-' + VM_ID

lc.log_function('INFO', 40 * "#")

# INITIALIZE_CONTAINER
init = {'name': VM_NAME, 'source': {'type': 'none'}}
try:
    container = client.containers.create(init, wait=True)
except LXDAPIException as lxdapie:  # probably this container already exists
    container = client.containers.get(VM_NAME)
apply_profile(profile, container)

# BOOT_CONTAINER
try:
    container.start(wait=True)
    container.config['user.xml']  # validate config
except LXDAPIException as lxdapie:
    if container.status == 'Running':
        container.stop(wait=True)
    DISK_TYPE = profile['DISK_TYPE']
    DISK_TARGET = profile['DISK_TARGET']
    num_hdds = profile['num_hdds']
    lc.container_wipe(num_hdds, container, DISK_TARGET, DISK_TYPE)
    lc.log_function('ERROR', 'container: ' + str(lxdapie))
    lc.sys.exit(1)

lc.vnc_start(VM_ID, profile['dicc'])
lc.clock(t0, VM_ID)
print VM_NAME
