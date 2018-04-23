#!/bin/bash

VM_ID=$1
VNC_PORT=$2
VNC_PASSWD=$3
counter=1

if [[ $VNC_PASSWD != None ]]; then
  VNC_PASSWD="-passwd $VNC_PASSWD"
fi

while [[ $(lxc info one-$VM_ID | grep Status | awk {'print $2'}) == "Running" ]]; do
  svncterm -timeout 0 $VNC_PASSWD -rfbport $VNC_PORT -c lxc exec one-$VM_ID login || ((counter=counter+1))
  if [[ $counter -eq 6 ]]; then exit
  fi
done

