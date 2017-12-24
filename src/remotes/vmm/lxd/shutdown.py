#!/usr/bin/python

import lxd_common as lc

t0 = lc.time()
client = lc.Client()

VM_ID = lc.sys.argv[1]
container = client.containers.get('one-' + VM_ID)

# READ_XML
dicc = lc.xml_start(container.config['user.xml'])
DISK_TYPE = lc.xml_query_list('DISK/TYPE', dicc)
DISK_TARGET = lc.xml_query_list('DISK/TARGET', dicc) # no need to read unless num_hdds > 1

# CONTAINER_SHUTDOWN
if len(lc.sys.argv) == 3:
    container.stop(force=True, wait=True)
else:
    container.stop(wait=True)

lc.container_wipe(container, DISK_TARGET, DISK_TYPE)
lc.clock(t0)
