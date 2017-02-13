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
import socket


# def vnc_babysiter(data):
#    if data['STATE'] == 'a':
#        VM_ID = data['NAME']
#        client = lc.Client()
#        container = client.containers.get(VM_ID)
#        dicc = lc.xml_start(container.config['user.xml'])
#        VNC_PORT = int(lc.xml_query_item('GRAPHICS/PORT', dicc))
#
#        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#        result = sock.connect_ex(('127.0.0.1', VNC_PORT))
#        if result != 0:
#            lc.vnc_start(VM_ID, dicc)
#        else:
#            pass


def print_data(data):
    monitor = 'STATE=%s' % (data['STATE'])

    if data['STATE'] == 'a':
        monitor += ' CPU=%s MEMORY=%s NETRX=%s NETTX=%s' % (
            data['USEDCPU'], data['USEDMEMORY'], data['NETRX'], data['NETTX'])

    return monitor


def print_all_vm_template(hypervisor):
    instance = hypervisor()
    try:
        vms = instance.get_all_vm_info()

        print 'VM_POLL=YES'

        for vm, info in vms.iteritems():
            id_number = -1

            if 'one-' in info['NAME']:
                id_number = info['NAME'].split('-')[1]

            string = "VM=[\n"
            string += "  ID=%s,\n  DEPLOY_ID=%s,\n" % (id_number, info['NAME'])

            # Wild VMs
            # try:
            #     string += "  VM_NAME=%s,\n  IMPORT_TEMPLATE=%s\n" % (info['VM_NAME'], info['TEMPLATE'])
            # except:
            #     pass

            monitor = print_data(info)

            string += '  POLL="%s" ]' % (monitor)

            print string

            # vnc_babysiter(info)
    except:
        return None

    # print string


def print_one_vm_info(hypervisor, vm_id):
    instance = hypervisor()
    try:
        info = instance.get_vm_info(vm_id)
        print print_data(info)
        # vnc_babysiter(info)
    except:
        return None


def print_all_vm_info(hypervisor):
    instance = hypervisor()
    try:
        vms = instance.get_all_vm_info()
    except:
        return None
    pass
