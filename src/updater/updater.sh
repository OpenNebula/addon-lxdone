#!/bin/bash

# This script updates the lxdone drivers scripts.
 
source $(dirname $0)/updater_config.sh

for i in $drivers; do
 	sshpass -p $password rsync -a --chmod=ugo=rwX $source/$i/ oneadmin@$destination/$i/
done 