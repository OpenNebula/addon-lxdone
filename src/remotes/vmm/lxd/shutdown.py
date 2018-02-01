#!/usr/bin/python

import lxd_common as lc

t0 = lc.time()
client = lc.Client()

VM_ID = lc.sys.argv[1]
container = client.containers.get('one-' + VM_ID)
dicc = lc.xml_start(container.config['user.xml'])

# CONTAINER_SHUTDOWN
if len(lc.sys.argv) == 3:
    container.stop(force=True, wait=True)
else:
    container.stop(wait=True)
lc.container_wipe(container, dicc)

lc.clock(t0)
