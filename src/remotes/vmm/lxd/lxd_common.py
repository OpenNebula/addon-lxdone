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

from __future__ import print_function
import os
import subprocess as sp
import sys
import xml.etree.ElementTree as ET
from time import time
from pylxd.client import Client
import isoparser


# MISC

def log_function(severity, message):
    sep = ': '
    print(severity + sep + os.path.basename(sys.argv[0]) + sep + message, file=sys.stderr)


def clock(t0, VM_ID):
    'Calculates and logs in the logfile the time passed since $t0'
    duration = str(time() - t0)
    log_function("INFO", 'Script executed in almost ' + duration + ' seconds')


def vnc_start(VM_ID, dicc):
    'If graphics are defined in the VM template, starts VNC server in the one-$VM_ID container shell'
    VNC_PORT = xml_query_item('GRAPHICS/PORT', dicc)
    if VNC_PORT:
        VNC_PASSWD = xml_query_item('GRAPHICS/PASSWD', dicc)
        try:
            if VNC_PASSWD:
                VNC_PASSWD = "-passwd " + VNC_PASSWD
            else:
                VNC_PASSWD = ""
            sp.Popen('bash /var/tmp/one/vmm/lxd/vnc.bash ' +
                     VM_ID + " " + VNC_PORT, shell=True)
        except Exception as e:
            # log_info(e, VM_ID)
            log_function("ERROR", e)


def container_wipe(num_hdds, container, DISK_TARGET, DISK_TYPE):
    'Deletes $container after unmounting and unmapping its related storage'
    if num_hdds > 1:
        for x in xrange(1, num_hdds):
            source = unmap(container.devices, DISK_TARGET[x])
            source = storage_lazer(source)
            storage_sysunmap(DISK_TYPE[x], source)
    storage_rootfs_umount(DISK_TYPE[0], container.config)
    container.delete()


# XML RELATED
def xml_start(xml):
    'Stores $xml file in $dicc dictionary'

    def xml_parse(root, dicc, way=""):
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

    tree = ET.parse(xml, parser=None)
    root = tree.getroot()
    dicc = {}
    xml_parse(root, dicc, way="")
    return dicc


def xml_query_list(value, dicc):
    'Tries to return a list with $value instances from $dicc'
    try:
        value = dicc['/VM/TEMPLATE/' + value]
    except:
        value = [None]
    return value


def xml_query_item(value, dicc):
    'Returns the first element of the list $value obtained by calling xml_query'
    value = xml_query_list(value, dicc)
    return value[0]


def xml_query_dict(value, id_list, dicc):
    'Tries to return a dict with $value instances from $dicc'
    try:
        value_list = xml_query_list(value, dicc)
        pos = 0
        value_dict = {}
        for iface in id_list:
            value_dict[iface] = value_list[pos]
            pos += 1
    except Exception:
        value_dict = {None}
    return value_dict


# STORAGE SIMPLE
def storage_sysmap(DISK_ID, DISK_TYPE, DISK_SOURCE, VM_ID, DS_ID, DISK_CLONE):
    'Maps a $DISK_SOURCE device into the host corresponding block device, CEPH, LVM or FILESYSTEM'

    def storage_pre(command):
        blockdev = sp.check_output(command, shell=True)
        return blockdev.strip('\n')

    disk = None
    if DISK_TYPE == "FILE":
        disk = "/var/lib/one/datastores/" + DS_ID + \
            "/" + VM_ID + "/" + 'disk.' + DISK_ID
        disk = storage_pre("losetup -f --show " + disk)
    elif DISK_TYPE == "BLOCK":
        pass
    elif DISK_TYPE == "RBD":
        if DISK_CLONE == 'YES':
            DISK_SOURCE = DISK_SOURCE + '-' + VM_ID + '-' + DISK_ID
        disk = storage_pre('rbd --id libvirt map ' + DISK_SOURCE)
    return disk


def storage_sysunmap(DISK_TYPE, source):
    'Unmaps a $source device from the host corresponding block device, CEPH, LVM or FILESYSTEM'
    if DISK_TYPE == "FILE":
        sp.call("losetup -d " + source, shell=True)
    elif DISK_TYPE == "BLOCK":
        pass
    elif DISK_TYPE == "RBD":
        sp.call('rbd unmap ' + source, shell=True)


def storage_lazer(device):
    'Returns the target device based on minor and major number'
    major = device['major']
    minor = device['minor']
    return sp.check_output('udevadm info -rq name /sys/dev/block/' + major + ':' + minor,
                           shell=True).strip('\n')


# STORAGE COMPOSED
def storage_rootfs_mount(VM_ID, DISK_TYPE, DS_ID, DISK_SOURCE, DISK_CLONE):
    'Mounts rootfs for container one-$VM_ID'
    source = storage_sysmap('0', DISK_TYPE, DISK_SOURCE,
                            VM_ID, DS_ID, DISK_CLONE)
    target = '/var/lib/lxd/containers/' + "one-" + VM_ID
    sp.call("mount " + source + " " + target, shell=True)
    return {'user.rootfs': source}


def storage_rootfs_umount(DISK_TYPE, container_config):
    'Unmounts the rootfs in $container_config and unmaps it from the host'
    source = container_config['user.rootfs']
    sp.call("umount " + source, shell=True)
    storage_sysunmap(DISK_TYPE, source)


def storage_context(container, contextiso):
    for i in contextiso.record().children:
        if i.is_directory is True:
            # FIXME: implement directory copy
            continue
        container.files.put('/mnt/' + i.name, i.content)


# LXD CONFIG MAPPING


def map_disk(DISK_TARGET, path):
    'Creates a dictionary for LXD containing $path disk configuration, $DISK_TARGET will be $path \
    inside the container'
    dev_stat = os.stat(path)
    major = str(os.major(dev_stat.st_rdev))
    minor = str(os.minor(dev_stat.st_rdev))
    return {DISK_TARGET: {'path': '/dev/' + DISK_TARGET, 'type': 'unix-block', 'minor': minor,
                          'major': major}}


def map_cpu(CPU):
    'Creates a dicitionary for LXD containing $CPU percentage per core assigned to the container'
    CPU = str(int(float(CPU) * 100)) + '%'
    return {'limits.cpu.allowance': CPU}


def map_vcpu(VCPU):
    'Creates a dicitionary for LXD containing $VCPU cores assigned to the container'
    if VCPU:
        return {'limits.cpu': VCPU}
    else:
        return {'user.warning': 'using_all_CPUs'}


def map_ram(MEMORY):
    'Creates a dicitionary for LXD containing $MEMORY RAM allocated'
    MEMORY = MEMORY + 'MB'
    return {'limits.memory': MEMORY}


def map_xml(xml):
    'Creates a dicitionary for LXD containing the path to $xml deployment file'
    return {'user.xml': xml}


def map_nic(nic_name, NIC_BRIDGE, NIC_MAC, NIC_TARGET):
    'Creates a dicitionary for LXD containing $nic_name network interface configuration'
    return {nic_name: {'name': nic_name, 'type': 'nic', 'hwaddr': NIC_MAC, 'nictype': 'bridged',
                       'parent': NIC_BRIDGE, 'host_name': NIC_TARGET}}


def unmap(container_devices, device_name):
    'Delete and returns $device_name from $container_devices'
    source = container_devices[device_name]
    del container_devices[device_name]
    return source
