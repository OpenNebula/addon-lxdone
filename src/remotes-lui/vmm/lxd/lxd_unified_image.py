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

import subprocess as sp

def uniimg_container_wipe(client, container):
    # get image's fingerprint
    fingerprint = container.config['volatile.base_image']

    container.delete(wait=True)

    # wipe image if no container using
    container_list = client.containers.all()
    if len(container_list) == 0:
        # no running container
        image = client.images.get(fingerprint)
        image.delete()

    elif len(filter(lambda x: x.config['volatile.base_image'] == fingerprint, container_list)) == 0:
        # no container using this image
        image = client.images.get(fingerprint)
        image.delete()
