#!/usr/bin/python

import lxd_common as lc

t0 = lc.time()

DOMAIN = lc.sys.argv[1]
HOST = lc.sys.argv[2]
VM_ID = lc.sys.argv[3]

client = lc.Client()
container = client.containers.get(DOMAIN)
dicc = lc.xml_start(container.config['user.xml'])

# CONTAINER_SHUTDOWN
if len(lc.sys.argv) == 3:
    container.stop(force=True, wait=True)
else:
    container.stop(wait=True)
lc.container_wipe(container, dicc)

lc.clock(t0)
