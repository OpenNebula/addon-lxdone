#!/bin/bash

VM_ID=$1
VNC_PORT=$2
# VNC_PASSWD=$3
counter=1

while [[ $(lxc info one-$VM_ID | grep Status | awk {'print $2'}) == "Running" ]]; do
        svncterm -timeout 0 -rfbport $VNC_PORT -c lxc exec one-$VM_ID login || ((counter=counter+1))
        if [[ $counter -eq 6 ]]; then exit
        fi
done

