# Installation & Configuration Guide
The purpose of this guide is to create a fully functional working environment. You will be able to manage **LXD** containers in at least one virtualization node through the web interface in the frontend. For the list of supported features see [Readme](https://github.com/OpenNebula/addon-lxdone/blob/master/README.md#features).

## Table of Contents

<!-- MarkdownTOC -->

- [1 - Frontend setup](#1---frontend-setup)
    - [1.1 Installation](#11-installation)
    - [1.2 LXDoNe integration](#12-lxdone-integration)
- [2 - Virtualization Node setup](#2---virtualization-node-setup)
    - [2.1 Install required packages](#21-install-required-packages)
    - [2.2 VNC server](#22-vnc-server)
    - [2.3 LXD Bridge \(optional\)](#23-lxd-bridge-optional)
    - [2.4 oneadmin](#24-oneadmin)
    - [2.5 Loop devices](#25-loop-devices)
    - [2.6 LXD](#26-lxd)
- [3 - Virtual Appliance](#3---virtual-appliance)
    - [3.1 Copying from an image server](#31-copying-from-an-image-server)
    - [3.2 Export](#32-export)
- [4 - Usage](#4---usage)
    - [4.1 Image Upload](#41-image-upload)
    - [4.2 Virtualization node](#42-virtualization-node)
    - [4.4 Virtual network](#44-virtual-network)
    - [4.5 Template creation](#45-template-creation)
    - [4.6 Deploy](#46-deploy)

<!-- /MarkdownTOC -->


<a name="1---frontend-setup"></a>
# 1 - Frontend setup

<a name="11-installation"></a>
## 1.1 Installation

Follow [OpenNebula Deployment Guide](https://docs.opennebula.org/5.2/deployment/opennebula_installation/frontend_installation.html) to deploy a fully functional OpenNebula frontend.

<a name="12-lxdone-integration"></a>
## 1.2 LXDoNe integration
**LXDoNe** is a set of scripts functioning as virtualization and monitorization drivers, so they have to be integrated to the ***frontend***. 


<a name="141-drivers"></a>
### 1.2.1 Drivers
Download the addon:

```bash
git clone https://github.com/OpenNebula/addon-lxdone.git
cd addon-lxdone
```

Copy scripts to oneadmin drivers directory: 

```
cp -rpa src/remotes/ /var/lib/one/
```

Set the appropriate permissions

```
sudo cd /var/lib/one/remotes/
sudo chown -R oneadmin:oneadmin vmm/lxd im/lxd*
sudo chmod 755 -R vmm/lxd im/lxd*
sudo chmod 644 im/lxd.d/collectd-client.rb
```

### Optional. Add support for 802.1Q driver (VLANs).
Replace /var/lib/one/remotes/vnm.rb file.

```
cp -rpa src/one_wait/nic.rb /var/lib/one/remotes/vnm/nic.rb
sudo chown oneadmin:oneadmin /var/lib/one/remotes/vnm/nic.rb
sudo chmod 755 /var/lib/one/remotes/vnm/nic.rb
```

#### Note
> A pull request was made to add this functionality to OpenNebula's official Network Driver.

<a name="142-enable-lxd"></a>
### 1.2.2 Enable LXD

Modify /etc/one/oned.conf.
Under **Information Driver Configuration** add this:

```
#-------------------------------------------------------------------------------
# lxd Information Driver Manager Configuration
# -r number of retries when monitoring a host
# -t number of threads, i.e. number of hosts monitored at the same time
#-------------------------------------------------------------------------------
IM_MAD = [ NAME = "lxd",
EXECUTABLE = "one_im_ssh",
ARGUMENTS = "-r 3 -t 15 lxd" ]
#-------------------------------------------------------------------------------
```

Under **Virtualization Driver Configuration** add this:

```
#-------------------------------------------------------------------------------
# lxd Virtualization Driver Manager Configuration
# -r number of retries when monitoring a host
# -t number of threads, i.e. number of actions performed at the same time
#-------------------------------------------------------------------------------
VM_MAD = [ NAME = "lxd",
EXECUTABLE = "one_vmm_exec",
ARGUMENTS = "-t 15 -r 0 lxd",
KEEP_SNAPSHOTS = "yes",
TYPE = "xml",
IMPORTED_VMS_ACTIONS = "migrate, live-migrate, terminate, terminate-hard, undeploy, undeploy-hard, hold, release, stop, suspend, resume, delete, delete-recreate, reboot, reboot-hard, resched, unresched, poweroff, poweroff-hard, disk-attach, disk-detach, nic-attach, nic-detach, snap-create, snap-delete"]
#-------------------------------------------------------------------------------

```

<a name="2---virtualization-node-setup"></a>
# 2 - Virtualization Node setup

Follow [KVM Node Installation](https://docs.opennebula.org/5.2/deployment/node_installation/kvm_node_installation.html#), up to [step 6](https://docs.opennebula.org/5.2/deployment/node_installation/kvm_node_installation.html#step-6-storage-configuration). If you want to use Ceph to store Virtual Images, follow [Ceph Datastore Guide](https://docs.opennebula.org/5.2/deployment/open_cloud_storage_setup/ceph_ds.html) and configure it just as you would for KVM.

<a name="21-install-required-packages"></a>
## 2.1 Install required packages

```
sudo apt install lxd lxd-tools criu bridge-utils python-pylxd python-ws4py python-pip
```

#### Note
> Be sure to have **pylxd 2.0.5**, or the driver **won't work properly**. Check the last output of the command below. You can find it on xenial-updates repositories.

```
sudo apt show python-pylxd | grep 2.0.5 | grep 2.0.5
```

Install isoparser by pip

```
sudo pip install isoparser
```

<a name="22-vnc-server"></a>
## 2.2 VNC server
**LXDoNe** uses **svncterm** by **dealfonso@github** as **VNC** server. This package enables the **VNC** option in the VM template definition. It's already compiled for Ubuntu 16.04. Install the required dependencies from repositories.

```
sudo dpkg -i svncterm_1.2-1ubuntu_amd64.deb
```

<a name="23-lxd-bridge-optional"></a>
## 2.3 LXD Bridge (optional)
**LXD** comes by default with an optional bridge called **lxdbr0**, it offers ease of use for containers networking and provides DHCP suport. We can use this bridge alternative configuration to standard OpenNebula networking:

```
sudo echo -e " USE_LXD_BRIDGE="true" \n
LXD_BRIDGE="lxdbr0" \n
UPDATE_PROFILE="true" \n
LXD_CONFILE="" \n
LXD_DOMAIN="lxd" \n
LXD_IPV4_ADDR="192.168.1.1" \n
LXD_IPV4_NETMASK="255.255.255.0" \n
LXD_IPV4_NETWORK="192.168.1.1/24" \n
LXD_IPV4_DHCP_RANGE="192.168.1.2,192.168.1.254" \n
LXD_IPV4_DHCP_MAX="252" \n
LXD_IPV4_NAT="true" \n
LXD_IPV6_ADDR="" \n
LXD_IPV6_MASK="" \n
LXD_IPV6_NETWORK="" \n
LXD_IPV6_NAT="false" \n
LXD_IPV6_PROXY="false" " > /etc/default/lxd-bridge
# service lxd-bridge restart
```

<a name="24-oneadmin"></a>
## 2.4 oneadmin

Allow oneadmin to execute commands as root and add it to lxd group

```
sudo echo "oneadmin ALL= NOPASSWD: ALL" >> /etc/sudoers
sudo adduser oneadmin lxd
```

<a name="25-loop-devices"></a>
## 2.5 Loop devices

Every file system image used by **LXDoNe** will require one ***loop device***. The default limit for ***loop devices*** is 8, so it needs to be increased.

```
sudo echo "options loop max_loop=128" >> /etc/modprobe.d/local-loop.conf
sudo echo "loop" >> /etc/modules
sudo depmod
```

<a name="26-lxd"></a>
## 2.6 LXD

<a name="261-daemon"></a>
### 2.6.1 Daemon
This is the daemon configuration we'll use

```
sudo lxd init --auto \
--storage-backend dir \
--network-address 0.0.0.0 \
--network-port 8443 \
--trust-password password
```

<a name="262-lxd-profile"></a>
### 2.6.2 LXD Profile
Containers inherit properties from a profile.

#### Network
The default profile contains a network device, we'll remove this one as it's not managed by OpenNebula.

```
sudo lxc profile device remove default eth0
```

#### Security & Nesting:

We moved from privileged containers to unprivileged containers by default and supported nesting since LXDoNe 1707. More of this [here](http://linuxcontainers.org/lxc/security/#privileged-containers) and [here](https://insights.ubuntu.com/2016/04/15/lxd-2-0-lxd-in-lxd-812/). It is no longer required the use of a default profile with ***security.privileged: true***.

<a name="3---virtual-appliance"></a>
# 3 - Virtual Appliance
A virtual appliance is available at the [marketplace](https://marketplace.opennebula.systems/appliance/7dd50db7-33c4-4b39-940c-f6a55432622f). Also, we've uploaded a base container to [google drive](http://https://drive.google.com/uc?export=download&confirm=FkpQ&id=0B97YSqohwcQ0bTFRUE5RMmphT1U). The image creation tweaks are covered in depth [here](Image.md), but we wont update it anymore, for simplicity we show just a method in this guide. You can SKIP to [step 4](Setup.md#4---usage) if google drive or marketplace works for you, we STRONGLY recommend it. Also there is a script [build-img.sh](image-handling/build-img.sh) that automates the process.

<a name="31-copying-from-an-image-server"></a>
## 3.1 Copying from an image server
Copy an image into local image store.

```
lxc image copy ubuntu: local: --alias ubuntu1604
```

<a name="32-export"></a>
## 3.2 Export
Export the image from LXD local image store to current directory. Maybe will create two tarballs.

```
lxc image export ubuntu1604
ls -l
-rw------- 1 oneadmin oneadmin 126715472 May 30 15:29 8fa08537ae51c880966626561987153e72d073cbe19dfe5abc062713d929254d.tar.xz
-rw------- 1 oneadmin oneadmin       840 May 30 15:29 meta-8fa08537ae51c880966626561987153e72d073cbe19dfe5abc062713d929254d.tar.xz
```

### 3.3 Extract tarballs
```
sudo mkdir -p image/rootfs
cd image
sudo tar xvpf ../8fa08537ae51c880966626561987153e72d073cbe19dfe5abc062713d929254d.tar.xz -C rootfs
sudo tar xvpf ../meta-8fa08537ae51c880966626561987153e72d073cbe19dfe5abc062713d929254d.tar.xz
ls -l image
-rw-r--r--  1 root   root   1566 May 16 15:26 metadata.yaml
drwxr-xr-x 22 root   root   4096 May 31 14:29 rootfs
drwxr-xr-x  2 root   root   4096 May 16 15:26 templates
```

### 3.4 Install one-context package (optional)
Download one-context_*.deb package if you use OpenNebula CONTEXT scripts instead of cloud-init

```
wget https://github.com/OpenNebula/addon-context-linux/releases/download/v5.0.3/one-context_5.0.3.deb
sudo mv one-context_5.0.3.deb rootfs/
```

Chroot to rootfs/

```
sudo chroot rootfs/ /bin/bash
```

Install one-context and disable cloud-init

```
sudo dpkg -i ./one-context_5.0.3.deb
sudo systemctl disable cloud-init.service cloud-init-local.service cloud-final.service cloud-config.service
exit
```

Overwrite modified context

```
sudo cp -p /path/to/addon-lxdone/src/one-wait/10-network rootfs/etc/one-context.d
sudo cp -p /path/to/addon-lxdone/src/one-wait/one-contextd rootfs/usr/sbin
```
Set the appropriate permissions

```
sudo chown root:root rootfs/usr/sbin/one-contextd rootfs/etc/one-context.d/10-network
sudo chmod 755 rootfs/usr/sbin/one-contextd rootfs/etc/one-context.d/10-network
```

### 3.5 Block Device creation
At the end of every one of the previous methods you'll have to save your work in a raw image that will be uploaded to a Datastore. So regardless the method you choose you'll have to do this before beginning the method, except for **LXCoNe**:

```bash
truncate -s <size_in_GB>G /var/tmp/lxdone.img
loop=$(sudo losetup --find --show /var/tmp/lxdone.img)
mkfs.ext4 $loop
mount $loop /mnt/
```

Check you are in the image root folder cheking the output of ***ls -lh*** :

```bash
total 16K
-r--------  1 root root 1.5K Jan 31 00:38 backup.yaml
-rw-r--r--  1 root root 1.4K Jan 26 16:36 metadata.yaml
drwxr-xr-x 21 root root 4.0K May 15 15:49 rootfs
drwxr-xr-x  2 root root 4.0K Nov  2  2016 templates
```

And copy cotents to block device

```
sudo cp -rpa * /mnt/
sudo umount $loop
sudo losetup -d $loop
```

<a name="4---usage"></a>
# 4 - Usage
This is a set of basic usage, there are lots of extra features to use. For the list of supported features see [Readme](README.md).

<a name="41-image-upload"></a>
## 4.1 Image Upload

Upload the Virtual Appliance to OpenNebula.

<a name="required-data"></a>
### Required data:
* Name
* Type: Select **Operating System image**
* Image location

![](picts/Images.png)

<a name="42-virtualization-node"></a>
## 4.2 Virtualization node

<a name="required-data-1"></a>
### Required data:
* Type: Select **Custom**
* Name
* Under Drivers:
    * Virtualization: Select **Custom**
    * Information: Select **Custom**
    * Custom VMM_MAD: Enter **lxd**
    * Custom IM_MAD: Enter **lxd**

![](picts/Host.png)

<a name="44-virtual-network"></a>
## 4.4 Virtual network

<a name="required-data-2"></a>
### Required data:
* General:
    * Name
* Conf:
    * Bridge. **br0** or **lxdbr0** in this case.
* Addresses:
    * Select **IPv4** if using **br0**, **Ethernet** if using **lxdbr0** or an external **DHCP** service
    * First **IP/MAC address**
    * Size

![](picts/nic.png)

<a name="45-template-creation"></a>
## 4.5 Template creation

<a name="required-data-3"></a>
### Required data:
* General:
    * Name
    * Memory (ex. 32MB)
    * CPU (ex. 0.1)
    * VCPU (optional ex. 1)
* Storage:
    * Select on Disk 0 the Virtual Appliance (You must set as Disk 0 an OS image)

#### Note
> VCPU stands for the amount of cores the container can use, if the container if you leave it blank, the container will use all the cores up to a fraction defined by CPU.
> ex. for a host with 8 CPUs, if the VM template states 2 VCPU, then the container has 2/8 CPUs allocated.

### Optional data:
* Network:
    * Select one or many network interfaces. They will appear inside the container configured.
* Input/Output:
    * Select **VNC** under graphics.
    * Server port
* Other:
    * LXD_SECURITY_NESTING = '**true**' for creating containers inside the container.
    * LXD_SECURITY_PRIVILEGED = '**true**' for make the container privileged.


![](picts/template.png)

![Alt text](/home/dann1/Projects/addon-lxdone/picts/lxd-security.png "Optional title") 

<a name="46-deploy"></a>
## 4.6 Deploy
Click **Instances** --> **VMs** --> **ADD**.
Select the corresponding template and click **Create**. Then wait for the scheduler to execute the drivers. In the Log section there will be additional information like the time spent on executing actions scripts and errors if they occur.
![](picts/log.png)

Also if you use VNC, the graphic session will start in the login prompt inside the container. noVNC should look like this:
![](picts/vnc2.png)
