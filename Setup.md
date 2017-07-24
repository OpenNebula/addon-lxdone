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
    - [2.4 oneadmin](#24-oneadmin)
    - [2.5 Loop devices](#25-loop-devices)
    - [2.6 LXD](#26-lxd)
- [3 - Virtual Appliance](#3---virtual-appliance)
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

Follow [frontend installation](https://docs.opennebula.org/5.2/deployment/opennebula_installation/frontend_installation.html) in OpenNebula deployment guide.

<a name="12-lxdone-integration"></a>
## 1.2 LXDoNe integration
**LXDoNe** is a set of scripts operating as virtualization and monitorization drivers, so they have to be integrated to the ***frontend***. 

<a name="141-drivers"></a>
### 1.2.1 Drivers
[Download the latest release](https://github.com/OpenNebula/addon-lxdone/releases/tag/v5.2-4.1) and untar it:

```bash
tar -xf <filename>.tar.gz
```

Copy scripts to oneadmin drivers directory: 

```
cd <filename>
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
Replace /var/lib/one/remotes/vnm.rb file for ur modified version.

```
cp -rpa src/one_wait/nic.rb /var/lib/one/remotes/vnm/nic.rb
sudo chown oneadmin:oneadmin /var/lib/one/remotes/vnm/nic.rb
sudo chmod 755 /var/lib/one/remotes/vnm/nic.rb
```

#### Note
> A pull request was made to OpenNebula's official Network Driver to add this functionality by default.

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

Restart OpenNebula

```
sudo systemctl restart opennebula
```

<a name="2---virtualization-node-setup"></a>
# 2 - Virtualization Node setup

Follow [KVM Node Installation](https://docs.opennebula.org/5.2/deployment/node_installation/kvm_node_installation.html#), up to [step 6](https://docs.opennebula.org/5.2/deployment/node_installation/kvm_node_installation.html#step-6-storage-configuration). If you want to use Ceph to store Virtual Images, follow [Ceph Datastore Guide](https://docs.opennebula.org/5.2/deployment/open_cloud_storage_setup/ceph_ds.html) and configure it just as you would for KVM.

#### Note
> ***opennebula-node*** package installs kvm-required software. You may remove most of them and/or disable services like libvirt-bin as they aren't required by LXD. Don't remove libvirt package, it is required for ceph storage.

<a name="21-install-required-packages"></a>
## 2.1 Install required packages

```
sudo apt install lxd lxd-tools python-pylxd/xenial-updates criu bridge-utils python-ws4py python-pip
```

#### Note
> Be sure to have **pylxd 2.0.5**, or the driver **won't work properly**.

Install isoparser by pip

```
sudo pip install isoparser
```

<a name="22-vnc-server"></a>
## 2.2 VNC server
**LXDoNe** uses **svncterm** by **dealfonso@github** as **VNC** server. This enables the **VNC** option in the VM template definition. We compiled and provided it for Ubuntu 16.04 in our releases. [Download it](https://github.com/OpenNebula/addon-lxdone/releases/tag/v5.2-4.1) and install the required dependencies from repositories.

```
sudo dpkg -i <source_path_to>/svncterm_1.2-1ubuntu_amd64.deb
```

<a name="24-oneadmin"></a>
## 2.4 oneadmin

Allow oneadmin to execute commands as root and add it to lxd group. Run as root:

```
echo "oneadmin ALL= NOPASSWD: ALL" >> /etc/sudoers
adduser oneadmin lxd
```

<a name="25-loop-devices"></a>
## 2.5 Loop devices

Every file system image used by **LXDoNe** will require one ***loop device***. The default limit for ***loop devices*** is 8, so it needs to be increased. Run as root:

```
echo "options loop max_loop=128" >> /etc/modprobe.d/local-loop.conf
echo "loop" >> /etc/modules-load.d/modules.conf
depmod
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
The default profile contains a network device, we'll remove this one as isn't managed by OpenNebula.

```
lxc profile device remove default eth0
```

#### Security & Nesting:

We moved from privileged containers to unprivileged containers by default and supported nesting since LXDoNe 5.2-4. More about this [here](http://linuxcontainers.org/lxc/security/#privileged-containers) and [here](https://insights.ubuntu.com/2016/04/15/lxd-2-0-lxd-in-lxd-812/). It is no longer required the use of a default profile with ***security.privileged: true***. Remove it if you had it:

```
lxc profile unset default security.privileged
```

### 2.6.3 User IDs

Check your ***/etc/subuid*** and ***/etc/subgid*** files has the following entries for lxd and root.

```
lxd:100000:65536
root:100000:65536
```

<a name="3---virtual-appliance"></a>
# 3 - Virtual Appliance
A virtual appliance is available at the [marketplace](https://marketplace.opennebula.systems/appliance/7dd50db7-33c4-4b39-940c-f6a55432622f). Also, we've uploaded a base container to online storage service providers. This is a compressed raw block tarball, just extract it before uploading to OpenNebula. You'll have a 1GB image, if you require more space, just copy the contents (keeping the same file permissions and ownership) to a bigger block device. The team user has *team* password:

- [google drive](https://drive.google.com/open?id=0B6vgzbpLofKjbXFzTjI1QmZ4X1U)
- [mega](https://mega.nz/#!U8pXxBpI!2UjFmQO8Fr8hz5oHt7z6QeIqYR3ziZ74OcNP1HByO4c)
- [dropbox](https://www.dropbox.com/s/p9s1tzc47tpgxqg/lxdone-5.2-4.1.img.tar.xz?dl=0)

<!-- You can generate your custom image following [this](Image.md) but we encourage you to use the ones we've uploaded, since it can get a bit tricky. -->

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
