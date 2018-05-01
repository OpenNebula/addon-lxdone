#!/bin/bash

# This script updates the lxdone drivers scripts.

function manual() {
  local ANOTHER="YES"
  
  read -p "Path to drivers: " SOURCE
  
  while [[ ! -d "$SOURCE" ]]; do
    read -p "Valid path: " SOURCE
  done
  
  while [[ $ANOTHER == "YES" ]]; do
    
    read -p "IP: " IP
    while ! valid_ip $IP; do
      read -p "Valid IP: " IP
    done
    
    read -p "Password: " -s PASSWORD1
    echo ""
    read -p "Retype password: " -s PASSWORD2
    echo ""
    
    while [[ $PASSWORD1 != $PASSWORD2 ]]; do
      echo -e "Sorry, passwords do not match \n"
      read -p "Password: " -s PASSWORD1
      echo ""
      read -p "Retype password: " -s PASSWORD2
      echo ""
    done
    echo ""
    
    for i in $DRIVERS; do
      sshpass -p $PASSWORD rsync -a --chmod=ugo=rwX $SOURCE/$i/ oneadmin@${IP}:/var/tmp/one/$i/
    done
    
    read -p "Wanna update another node? [[YES] or N] " ANOTHER
    ANOTHER=${ANOTHER:-YES}
  done
}

function auto() {
  source $1
  
  for i in $DRIVERS; do
    sshpass -p $PASSWORD rsync -a --chmod=ugo=rwX $SOURCE/$i/ oneadmin@${IP}:/var/tmp/one/$i/
  done
}

function valid_ip() {
  local  IP=$1
  local  STAT=-1
  
  if [[ $IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    OIFS=$IFS
    IFS='.'
    IP=($IP)
    IFS=$OIFS
    [[ ${IP[0]} -le 255 && ${IP[1]} -le 255 \
    && ${IP[2]} -le 255 && ${IP[3]} -le 255 ]]
    STAT=$?
  fi
  return $STAT
}

REQUIRED_PKG=$(command -v sshpass)

if [[ ! $REQUIRED_PKG ]]; then
  echo "Install sshpass"
  exit 0
fi

DRIVERS="im vmm"

if [[ $1 ]]; then
  echo "Used $1 as config file"
  auto $1
else
  manual
fi
