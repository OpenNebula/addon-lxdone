#!/usr/bin/python

import lxd_common as lc

t0 = lc.time()

DOMAIN = lc.sys.argv[1]
HOST = lc.sys.argv[2]
VM_ID = lc.sys.argv[3]

client = lc.Client()
container = client.containers.get(DOMAIN)
lc.log_function(lc.separator)

dicc = lc.xml_start(container.config['user.xml'])

# CONTAINER_SHUTDOWN
signal = lc.sys.argv[4].split("/")[-1]
if signal == "cancel":
    container.stop(force=True, wait=True)
elif signal == "shutdown":
    container.stop(wait=True)
else:
    lc.log_function("Unknown kill VM signal given", 'e')
    lc.sys.exit(1)
lc.container_wipe(container, dicc)

lc.clock(t0)
