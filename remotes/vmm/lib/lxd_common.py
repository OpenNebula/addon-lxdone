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

from pylxd.client import Client
import subprocess as sp
import xml.etree.ElementTree as ET
import sys
from datetime import datetime as dt
from time import time
import os

client = Client()
lxd_path = "/var/lib/lxd/containers/"


# MISC
def log_info(info, VM_ID):
    'Writes $info at the end of file /var/log/one/$VM_ID.log this is the Virtual Machine log file seen in Sunstone'
    log = open('/var/log/one/' + VM_ID + '.log', mode='a')
    moment = dt.today().strftime("%a %b %d %H:%M:%S %Y")
    log.write(moment + " " + str(info) + '\n')
    log.close()


def clock(VM_ID, t0):
    'Calculates and logs in the logfile the time passed since $t0  useful for timing scripts execution'
    duration = str(time() - t0)
    log_info('Script executed in almost ' + duration + ' seconds', VM_ID)


def vnc_start(VNC_PORT, VM_ID, VNC_PASSWD):
    'Starts VNC server with the login screen to the container $VM_ID'
    if VNC_PASSWD:
        VNC_PASSWD = "-passwd " + VNC_PASSWD
    else:
        VNC_PASSWD = ""
    sp.Popen("svncterm -timeout 0 " + VNC_PASSWD + " -rfbport " +
             VNC_PORT + " -c lxc exec one-" + VM_ID + " login &", shell=True)


# XML RELATED
def xml_parse(root, dicc, way=""):
    'Stores a $root defined xml in $dicc'
    new_way = way + "/" + root.tag
    value = []
    try:
        value = dicc[new_way]
    except:
        value = []
    value.append(root.text)
    dicc.__setitem__(new_way, value)
    for new_root in root._children:
        xml_parse(new_root, dicc, new_way)


def xml_start(xml):
    'Initializes the required variables for xml management and executes xml_parse'
    tree = ET.parse(xml, parser=None)
    root = tree.getroot()
    dicc = {}
    xml_parse(root, dicc, way="")
    return dicc


def xml_getvalue(value, dicc):
    'Tries to fetch $value in the xml stored in $dicc'
    try:
        value = dicc['/VM/TEMPLATE/' + value]
    except:
        value = [None]
    return value


def xml_getvalue_plus(dicc, value):
    'Returns the first element of the list obtained by calling xml_getvalue'
    value = xml_getvalue(dicc, value)
    return value[0]


# STORAGE SIMPLE
def storage_lazer(device):
    'Returns the device based on minor and major number'
    major = device['major']
    minor = device['minor']
    return sp.check_output('udevadm info -rq name /sys/dev/block/' + major + ':' + minor, shell=True).strip('\n')


def storage_pre(DISK_ID, DISK_TYPE, DISK_SOURCE, VM_ID, DS_ID, DISK_CLONE):
    'Returns opennebula image path'

    def storage_sysmap(command):
        'Maps a source device into the opennebula node corresponding block device, CEPH, LVM or FILESYSTEM'
        blockdev = sp.check_output(command, shell=True)
        return blockdev.strip('\n')

    disk = None
    if DISK_TYPE == "FILE":
        disk = "/var/lib/one/datastores/" + DS_ID + "/" + VM_ID + "/" + 'disk.' + DISK_ID
        disk = storage_sysmap("losetup -f --show " + disk)
    elif DISK_TYPE == "BLOCK":
        pass
    elif DISK_TYPE == "RBD":
        if DISK_CLONE == 'YES':
            DISK_SOURCE = DISK_SOURCE + '-' + VM_ID + '-' + DISK_ID
        disk = storage_sysmap('rbd --id libvirt map ' + DISK_SOURCE)
    return disk


def storage_sysunmap(DISK_TYPE, source):
    'Unmaps a source device from the opennebula node corresponding block device, CEPH, LVM or FILESYSTEM'
    if DISK_TYPE == "FILE":
        sp.call("losetup -d " + source, shell=True)
    elif DISK_TYPE == "BLOCK":
        pass
    elif DISK_TYPE == "RBD":
        sp.call('rbd unmap ' + source, shell=True)


# STORAGE COMPOSED
def storage_extra_map(VM_ID, DS_ID, DISK_ID, DISK_TYPE, DISK_SOURCE, DISK_CLONE, DISK_TARGET):
    'Prepares the container for mounting an extra block device, by mapping it into the opennebula node, then in the \
    container devices dictionary'
    source = storage_pre(DISK_ID, DISK_TYPE, DISK_SOURCE, VM_ID, DS_ID, DISK_CLONE)
    return map_disk(DISK_TARGET, source)


def storage_rootfs_mount(VM_ID, DISK_TYPE, DS_ID, DISK_SOURCE, DISK_CLONE):
    'Mounts rootfs for a given container'
    source = storage_pre('0', DISK_TYPE, DISK_SOURCE, VM_ID, DS_ID, DISK_CLONE)
    target = lxd_path + "one-" + VM_ID
    sp.call("mount " + source + " " + target, shell=True)
    return {'user.rootfs': source}


def storage_rootfs_umount(DISK_TYPE, source):
    'Unmounts the source block device and unmaps it from the opennebula node'
    sp.call("umount " + source, shell=True)
    storage_sysunmap(DISK_TYPE, source)


# LXD CONFIG MAPPING
def map_disk(DISK_TARGET, path):
    'Creates a dictionary for LXD containing disk configuration, path is /dev/$path'
    dev_stat = os.stat(path)
    major = str(os.major(dev_stat.st_rdev))
    minor = str(os.minor(dev_stat.st_rdev))
    return {DISK_TARGET: {'path': '/dev/' + DISK_TARGET, 'type': 'unix-block', 'minor': minor, 'major': major}}


def map_cpu(CPU):
    'Creates a dicitionary for LXD containing CPU percentage allowance'
    CPU = str(int(float(CPU) * 100)) + '%'
    return {'limits.cpu.allowance': CPU}


def map_vcpu(VCPU):
    'Creates a dicitionary for LXD containing the assignment of Cores to the container. If no value then all the cores \
    are assigned. VCPU is a list containing a single element'
    if VCPU:
        return {'limits.cpu': VCPU}
    else:
        return {'user.warning': 'using_all_CPUs'}


def map_ram(MEMORY):
    'Creates a dicitionary for LXD containing MEMORY configuration'
    MEMORY = MEMORY + 'MB'
    return {'limits.memory': MEMORY}


def map_xml(xml):
    'Creates a dicitionary for LXD containing the path to OpenNebula last used deployment.$ file. Useful for extra info'
    return {'user.xml': xml}


def map_nic(nic_name, NIC_BRIDGE, NIC_MAC, NIC_TARGET):
    'Creates a dicitionary for LXD containing nic configuration'
    # return {nic_name: {'name': nic_name, 'type': 'nic', 'hwaddr': NIC_MAC, 'nictype': 'bridged', 'parent': NIC_BRIDGE}}
    return {nic_name: {'name': nic_name, 'type': 'nic', 'hwaddr': NIC_MAC, 'nictype': 'bridged', 'parent': NIC_BRIDGE,
                       'host_name': NIC_TARGET}}
    # {'eth2': {'name': 'eth2', 'type': 'nic', 'hwaddr': NIC_MAC, 'nictype': 'bridged',
    #           'parent': NIC_BRIDGE, 'host_name': 'one-107-0'}}


def unmap(devices_dict, device_name):
    'Delete and returns the device_name dictionray from devices_dict'
    source = devices_dict[device_name]
    del devices_dict[device_name]
    return source
