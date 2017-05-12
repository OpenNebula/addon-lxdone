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
client = lc.Client()

# READ_XML
xml = lc.sys.argv[1]
dicc = lc.xml_start(xml)
VM_ID = dicc["/VM/ID"][0]

lc.log_info(70 * "-", VM_ID)

# INITIALIZE_CONTAINER
try:
    container = client.containers.create({'name': 'one-' + VM_ID, 'source': {'type': 'none'}}, wait=True)
except:
    container = client.containers.get('one-' + VM_ID)

# GENERAL_CONFIG
MEMORY = lc.map_ram(xqi('MEMORY', dicc))
CPU = lc.map_cpu(xqi('CPU', dicc))  # cpu percentage
VCPU = lc.map_vcpu(xqi('VCPU', dicc))  # cpu core
HOSTNAME = dicc["/VM/NAME"][0]
xml = lc.map_xml(xml)

# STORAGE_CONFIG
DS_ID = dicc["/VM/HISTORY_RECORDS/HISTORY/DS_ID"][0]
DISK_TYPE = xql('DISK/TYPE', dicc)
DISK_CLONE = xql('DISK/CLONE', dicc)
DISK_SOURCE = xql('DISK/SOURCE', dicc)

# rootfs
root_source = lc.storage_rootfs_mount(VM_ID, DISK_TYPE[0], DS_ID, DISK_SOURCE[0], DISK_CLONE[0])

# extra
num_hdds = len(DISK_TYPE)
DISK_TARGET = xql('DISK/TARGET', dicc)
if num_hdds > 1:
    DISK_ID = xql('DISK/DISK_ID', dicc)
    for x in xrange(1, num_hdds):
        source = lc.storage_sysmap(DISK_ID[x], DISK_TYPE[x], DISK_SOURCE[x], VM_ID, DS_ID, DISK_CLONE[x])
        disk = lc.map_disk(DISK_TARGET[x], source)
        container.devices.update(disk)

CONTEXT_DISK_ID = xqi('CONTEXT/DISK_ID', dicc)
if CONTEXT_DISK_ID:
    lc.storage_context_map(container, CONTEXT_DISK_ID, DISK_SOURCE, DS_ID, VM_ID)

# NETWORK_CONFIG
NIC = xql('NIC/NIC_ID', dicc)
if NIC[0]:
    NIC_BRIDGE = xqd('NIC/BRIDGE', NIC, dicc)
    NIC_MAC = xqd('NIC/MAC', NIC, dicc)
    NIC_TARGET = xqd('NIC/TARGET', NIC, dicc)
    for iface in NIC:
        i = str(iface)
        name = 'eth%s' % (iface)
        vm_nic = lc.map_nic(name, NIC_BRIDGE[i], NIC_MAC[i], NIC_TARGET[i])
        container.devices.update(vm_nic)

# SAVE_CONFIG
for x in MEMORY, CPU, VCPU, xml, root_source, {'user.hostname': HOSTNAME}:
    container.config.update(x)
container.save(wait=True)

# BOOT_CONTAINER
try:
    container.start(wait=True)
    container.config['user.xml']  # validate config
except Exception as e:
    if container.status == 'Running':
        container.stop(wait=True)
    lc.container_wipe(num_hdds, container, DISK_TARGET, CONTEXT_DISK_ID, DISK_TYPE)
    lc.log_info(e, VM_ID)
    lc.sys.exit(1)

lc.vnc_start(VM_ID, dicc)
lc.clock(t0, VM_ID)
print "one-" + VM_ID
