#!/usr/bin/env bash

dpkg --listfiles debootstrap > /dev/null 2>&1

if [[ $? -ne 0 ]]; then
    echo "debootstrap is required in order to crete container, press ENTER to continue"
    read
    apt install -y debootstrap
    if [[ $? -ne 0 ]]; then
        echo "failed to install debootstrap"
        exit -1
    fi
    echo
fi


for i in "size (default=600MB)" "release (default=xenial)" "repository (default=http://archive.ubuntu.com/ubuntu/)" "contexturl (default=https://github.com/OpenNebula/addon-context-linux/releases/download/v5.0.3/one-context_5.0.3.deb)"; do
    echo "Enter "$i
    var=$(echo $i | awk '{print $1}')
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

arch=$(uname --machine)

cp -pa ../metadata/metadata.yaml ./lxdone  
cp -rpa  ../metadata/templates ./lxdone

cp -p $(dirname $0)/shell-tweak/.[a-zA-Z]* ./lxdone/rootfs/root
chown root:root ./lxdone/rootfs/root/.[a-zA-Z]*

wget -P ./lxdone/rootfs/root $contexturl

if [[ $? -eq 0 ]]; then
    contextdeb=./lxdone/rootfs/root/$(basename $contexturl)
    if [[ -f $contextdeb ]]; then

        dpkg -i --root=./lxdone/rootfs/ --instdir=./lxdone/rootfs/ --admindir=./lxdone/rootfs/var/lib/dpkg ./$contextdeb

        cp -pa ../src/context/10-network ./lxdone/rootfs/etc/one-context.d 
        cp -pa ../src/context/one-contextd ./lxdone/rootfs/usr/sbin 
        
        chown root:root rootfs/usr/sbin/one-contextd rootfs/etc/one-context.d/10-network
        chmod 755 rootfs/usr/sbin/one-contextd rootfs/etc/one-context.d/10-network
    fi
fi

umount $img
losetup -d $img
