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

queue = open('/var/lib/lxd/lxdone_start_queue', mode='r')
deployments = queue.readlines()
queue.close()

for line in deployments:
    VM_ID = str(line.rpartition('/')[0]).rpartition('/')[2]
    try:
        lc.sp.call('python /var/tmp/one/vmm/lib/deploy ' + line)
        info = 'Power failure recovery SUCCESS'
    except Exception as e:
        info = e
    lc.log_info(VM_ID, info)
