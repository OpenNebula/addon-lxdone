# Frontend
## 1.1 Installation
(Follow original Setup.md)

## 1.2 Logs
(Follow original Setup.md)

## 1.4 LXDoNe integration
(Follow original Setup.md)

### 1.3 Enable LXD
(Follow original Setup.md)

### 1.4.1 Drivers

Copy scripts to oneadmin drivers directory:

```
$ sudo cp -rpa src/remotes/ /var/lib/one/
```

Overwrite some scripts by src/remotes-lui

```
$ cd src/remotes-lui
$ sudo cp -p vmm/lxd/* /var/lib/one/remotes/vmm/lxd
$ sudo cp -p im/lxd-probes.d/* /var/lib/one/remotes/im/lxd-probes.d
```
Set the appropriate permissions

```
$ cd /var/lib/one/remotes/
$ sudo chown -R oneadmin:oneadmin vmm/lxd im/lxd*
$ sudo chmod 755 -R vmm/lxd im/lxd*
$ sudo chmod 644 im/lxd.d/collectd-client.rb
```

### 1.4.1.1 Optional. Add support for 802.1Q driver (VLANs).
(Follow original Setup.md)

### 1.4.2 Enable LXD
(Follow original Setup.md)

# 2 - Virtualization Node setup
## 2.1 Install required packages

```
$ sudo apt install lxd lxd-tools criu bridge-utils python-pylxd nfs-common
$ sudo apt install python-pip

```

Install isoparser by pip

```
$ sudo pip install isoparser
```

## 2.2 VNC server (optional)
(Follow original Setup.md)

## 2.3 LXD Bridge (optional)
(Follow original Setup.md)

## 2.4 oneadmin

This driver does not require root privilege. Only needs to add oneadmin to lxd group.

```
% sudo adduser oneadmin lxd
```

## 2.5 Loop devices
This driver does not need loop devices. Skip this section.

## 2.6 LXD
### 2.6.1 Daemon
(Follow original Setup.md)

### 2.6.2 LXD Profile
(Follow original Setup.md)

#### 2.6.2.2 Security
This driver does not need security.privileged on default profile. Skip this section.

#### 2.6.2.3 Context (Optional)
This driver does not need raw.apparmor on default profile. Skip this section.

## 2.7 Log

# 3 - Virtual Appliance
This driver can use image exported from LXD.

## 3.1 Copying from an image server
Copy an image into local image store.

```
lxc image copy ubuntu: local: --alias ubuntu1604
```

## 3.2 Export
Export the image from LXD local image store to current directory. Maybe will create two tarballs.

```
$ lxc image export ubuntu1604
$ ls -l
-rw------- 1 oneadmin oneadmin 126715472 May 30 15:29 8fa08537ae51c880966626561987153e72d073cbe19dfe5abc062713d929254d.tar.xz
-rw------- 1 oneadmin oneadmin       840 May 30 15:29 meta-8fa08537ae51c880966626561987153e72d073cbe19dfe5abc062713d929254d.tar.xz
```

## 3.3 Create Unified image

### 3.3.1 Extract tarballs
```
$ sudo mkdir -p image/rootfs
$ cd image
$ sudo tar xvpf ../8fa08537ae51c880966626561987153e72d073cbe19dfe5abc062713d929254d.tar.xz -C rootfs
$ sudo tar xvpf ../meta-8fa08537ae51c880966626561987153e72d073cbe19dfe5abc062713d929254d.tar.xz
$ ls -l image
-rw-r--r--  1 root   root   1566 May 16 15:26 metadata.yaml
drwxr-xr-x 22 root   root   4096 May 31 14:29 rootfs
drwxr-xr-x  2 root   root   4096 May 16 15:26 templates
```

### 3.3.2 Install one-context package (optional)
Download one-context_*.deb package if you use OpenNebula CONTEXT scripts instead of cloud-init
```
$ wget https://github.com/OpenNebula/addon-context-linux/releases/download/v5.0.3/one-context_5.0.3.deb
$ sudo mv one-context_5.0.3.deb rootfs/
```

Chroot to rootfs/
```
$ sudo chroot rootfs/ /bin/bash
```

Install one-context and disable cloud-init
```
# dpkg -i ./one-context_5.0.3.deb
# systemctl disable cloud-init.service cloud-init-local.service cloud-final.service cloud-config.service
# exit
```

Overwrite two file fors LXD driver
```
$ sudo cp -p /path/to/remotes-lui/context/10-network rootfs/etc/one-context.d
$ sudo cp -p /path/to/remotes-lui/context/one-contextd rootfs/usr/sbin
```
Set the appropriate permissions
```
$ sudo chown root:root rootfs/usr/sbin/one-contextd rootfs/etc/one-context.d/10-network
$ sudo chmod 755 rootfs/usr/sbin/one-contextd rootfs/etc/one-context.d/10-network
```

### 3.3.3 Create unified tarball
```
$ cd ../
$ sudo tar cvJpf unifiedimage.tar.xz -C image/ metadata.yaml rootfs templates
```

### 3.3.4 Register image at OpenNebula
Send unified image tarball to Frontend and register as raw image
```
(on Frontend)
$ cat unifiedimage.txt
NAME          = "unifiedimage"
PATH          = "/var/tmp/unifiedimage.tar.xz"
TYPE          = "OS"
DESCRIPTION   = "Ubuntu LXD unified image"

$ oneimage create unifiedimage.txt -d default
```
