#!/usr/bin/env bash

dpkg --listfiles debootstrap > /dev/null 2>&1

if [[ $? -ne 0 ]]; then
    echo "debootstrap is required in order to crete container, press ENTER to continue"
    read
    apt install -y debootstrap
    if [[ $? -ne 0 ]]; then
        echo "failed to install debootstrap check your mirror configuration"
        exit -1
    fi
    echo
fi


for i in "size (default=600MB)" "release (default=xenial)" "repository (default=http://archive.ubuntu.com/ubuntu/)" "contexturl (default=https://github.com/OpenNebula/addon-context-linux/releases/download/v5.0.3/one-context_5.0.3.deb)"; do
    echo "Enter "$i
    var=`echo $i | awk '{print $1}'`
    read $var
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

if [[ -z $contexturl ]]; then
    contexturl=https://github.com/OpenNebula/addon-context-linux/releases/download/v5.0.3/one-context_5.0.3.deb
fi

truncate -s $size lxdone.img
img=$(losetup --find --show lxdone.img)
mkfs.ext4 $img
mkdir -p ./lxdone
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

mkdir -p ./lxdone/templates
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
echo "manual" > ./lxdone/templates/upstart-override.tpl

cp -p $(dirname $0)/bash-enhancements/.[a-zA-Z]* ./lxdone/rootfs/root
chown root:root ./lxdone/rootfs/root/.[a-zA-Z]*

wget -P ./lxdone/rootfs/root $contexturl
if [[ $? -eq 0 ]]; then
    contextdeb=./lxdone/rootfs/root/`basename $contexturl`
    if [[ -f $contextdeb ]]; then
        dpkg -i --root=./lxdone/rootfs/ --instdir=./lxdone/rootfs/ --admindir=./lxdone/rootfs/var/lib/dpkg ./$contextdeb
        sed -i 's%\(^[ \t]*ip link show | \).*$%\1awk '\''/^[0-9]+: [A-Za-z0-9@]+:/ { device=$2; gsub(/:/, "",device); split(device,dev,"\\@")} /link\\/ether/ { print dev[1]  " " $2 }'\''%' ./lxdone/rootfs/etc/one-context.d/10-network
    fi
fi

umount $img
losetup -d $img
