#!/usr/bin/env bash

dpkg --list debootstrap

if [[ $? -ne 0 ]]; then
    echo "debootstrap is required in order to crete container, press ENTER to continue"
    read
    apt install -y debootstrap
    if [[ $? -ne 0 ]]; then
        echo "failed to install debootstrap check your mirror configuration"
        exit -1
    fi
fi


for i in "size" "release" "repository" ; do
    echo "Enter "$i
    read $i
done

if [[ -z $release ]]; then
    release='xenial'
fi

if [[ -z $repository ]]; then
    repository='http://archive.ubuntu.com/ubuntu/'
fi

if [[ -z $size ]]; then
    size=600M
fi

truncate -s $size lxdone.img
img=$(losetup --find --show lxdone.img)
mkfs.ext4 $img
mkdir ./lxdone
mount $img ./lxdone

echo "creating $release linux filesystem from $repository this may take a while"
mkdir -p ./lxdone/rootfs
debootstrap $release ./lxdone/rootfs $repository

if [[ $? -ne 0 ]]; then
    umount $img
    losetup -d $img
    exit -1
fi

moment=$(date +%s)
arch=$(uname --machine)

cat << EOT > ./lxdone/metadata.yaml

{
    "architecture": "$arch",
    "creation_date": $moment,
    "templates": {
        "/etc/hostname": {
            "template": "hostname.tpl",
            "when": [
                "start"
            ]
        },
        "/etc/hosts": {
            "template": "hosts.tpl",
            "when": [
                "start"
            ]
        },
        "/etc/init/console.override": {
            "template": "upstart-override.tpl",
            "when": [
                "create"
            ]
        },
        "/etc/init/tty1.override": {
            "template": "upstart-override.tpl",
            "when": [
                "create"
            ]
        },
        "/etc/init/tty2.override": {
            "template": "upstart-override.tpl",
            "when": [
                "create"
            ]
        },
        "/etc/init/tty3.override": {
            "template": "upstart-override.tpl",
            "when": [
                "create"
            ]
        },
        "/etc/init/tty4.override": {
            "template": "upstart-override.tpl",
            "when": [
                "create"
            ]
        }
    }
}

EOT

mkdir ./lxdone/templates
cat << EOT > ./lxdone/templates/hosts.tpl
127.0.0.1   localhost
127.0.1.1   {{ config_get("user.hostname", "lxdone")}}

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

EOT

echo "{{ config_get("user.hostname", "lxdone")}}" > ./lxdone/templates/hostname.tpl
Pecho "manual" > ./lxdone/templates/upstart-override.tpl

cp -rpa $(dirname $0)/bash-enhancements/* ./lxdone/rootfs/

umount $img
losetup -d $img
