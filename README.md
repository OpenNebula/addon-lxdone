# LXDoNe

<a href="https://github.com/OpenNebula/addon-lxdone"><img src="picts/LXDoNe-logo-final.png" align="left" hspace="10" vspace="6"></a>

<br />

[![LXDoNe](https://img.shields.io/badge/release-1707-3c97f3.svg?style=flat-square)](https://github.com/OpenNebula/addon-lxdone/releases)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://twitter.com/intent/tweet?text=I%20want%20freedom.%20I%20want%20efficiency.%20Faster%20private%20clouds%20for%20everyone.%20%23LXDoNe%20%2B%20%40opennebula%20%3D%20performance%20⚡️%20https%3A%2F%2Fgithub.com/OpenNebula/addon-lxdone%2F&source=webclient)

[![LXD](https://img.shields.io/badge/lxd-LTS-orange.svg?style=flat-square)](https://linuxcontainers.org/lxd/)
[![Ceph](https://img.shields.io/badge/ceph-LTS-red.svg?style=flat-square)](https://ceph.com)
[![OpenNebula](https://img.shields.io/badge/one-5.2.1-blue.svg?style=flat-square)](https://opennebula.org)

[![pylxd](https://img.shields.io/badge/pylxd-2.0.5-brightgreen.svg?style=flat-square)](https://pylxd.readthedocs.io/en/stable/)
[![VNC](https://img.shields.io/badge/svncterm-1.2-yellow.svg?style=flat-square)](https://github.com/dealfonso/svncterm)

<br />
<br />

# Description

**LXDoNe** is an addon for OpenNebula to manage **LXD** Containers. It fits in the Virtualization and Monitorization Driver section according to OpenNebula's Architecture. It uses the **pylxd** API for several container tasks. This addon is the continuation of [LXCoNe](https://github.com/OpenNebula/addon-lxcone/), an addon for **LXC**. Check the [blog entry](https://opennebula.org/lxdone-lightweight-virtualization-for-opennebula/) in OpenNebula official site.

[LXD](https://linuxcontainers.org/lxd/) is a daemon which provides a REST API to drive **LXC** containers. Containers are lightweight OS-level Virtualization instances, they behave like Virtual Machines but don't suffer from hardware emulation processing penalties by sharing the kernel with the host. They run bare-metal-like, simple containers can boot up in 2 seconds consuming less than 32MB of RAM and a minimal fraction of a CPU Core. Check out this [performance comparison against KVM](https://insights.ubuntu.com/2015/05/18/lxd-crushes-kvm-in-density-and-speed/) if you don't know much about LXD.

# Development & Contribution
When contributing make pull requests to the feature branch for the next release, don't commit to master branch 
If you want to contribute feel free to request new features, check first TODO. Check the [Flowchart](picts/flow_chart) to get a bettter understanding of the driver internals, pictures starting with **one-** ex. [one-deploy.png](picts/flow_chart/one-deploy.png) ressemble the scripts overview. The action scripts are written in python, there is a script  [lxd_common.py](src/remotes/vmm/lxd/lxd_common.py) containing lots of functions used by the action scripts ex. [lxd_common.py](src/remotes/vmm/lxd/deploy.py) which is executed when starting a VM, tus reducing the code, if you want to add code and it could be used by several action scripts then add it here.

## Developers

### Leaders
- **Sergio Vega Gutiérrez** [![champion](https://img.shields.io/badge/one-champion-blue.svg?style=flat-square)](https://opennebula.org/community/community-champions/) [sergiojvg92 at gmail.com](mailto:sergiojvg92@gmail.com?subject=LXDoNe)
- **José Manuel de la Fé Herrero** [jmdelafe92 at gmail.com](mailto:jmdelafe92@gmail.com?subject=LXDoNe)
- **Daniel Clavijo Coca** [dann1telecom at gmail.com](mailto:dann1telecom@gmail.com?subject=LXDoNe)

### Contributors
- **Akihiko Ota**     [@sw37th]

# Compatibility
**LXDoNe** is not an update of **LXCoNe** so your old containers won't be manageable out of the box, but you can  adapt them to the new image format, read [Virtual Appliance](Image.md).

## Tested OpenNebula versions
[![OpenNebula](https://img.shields.io/badge/one-5.2.1-blue.svg?style=flat-square)](https://opennebula.org)
[![OpenNebula](https://img.shields.io/badge/one-5.2.0-blue.svg?style=flat-square)](https://opennebula.org)

## Tested Linux Distributions
[![ubuntu](https://img.shields.io/badge/ubuntu-1604-orange.svg?style=flat-square)](https://ubuntu.com)

# Setup
Check the [Setup Guide](Setup.md)  to deploy a working scenario.

# Features
## 1702
- Life cycle control:
    - Start and Poweroff
    - Reboot and Reset
    - Suspend and Resume
- Monitorization:
    - CPU
    - RAM
    - Status
    - Network Traffic
- Resource Limitation:
    - RAM
    - CPU
    - VCPU
- Log scripts execution time duration
- Deploy container with several disks
- Deploy container with several NICs
- Storage Backends:
    - Ceph
    - Filesystem
- VNC (beta)
- Specify target device for extra disks
- Contextualization compatibility
- 802.1Q network driver compatibility

## 1703
- Virtual Appliance creation script

## 1705 
- NIC Hotplug
- Virtual Appliance uploaded to [google drive](https://drive.google.com/uc?export=download&confirm=FkpQ&id=0B97YSqohwcQ0bTFRUE5RMmphT1U)
- Enhanced buildimg.sh, thanks @sw37th
    + Bugfixes
    + Included auto-contextualization

## 1707
- [VNC fixed](https://github.com/OpenNebula/addon-lxdone/issues/6)
- Context reworked
- Logs reworked
- Allow use of LXD feaures in VM Template:
    - privileged/unprivileged containers
    - nesting
- vmm scripts execution times reduced 40-60% 

## TODO
- Full live VM configurations 
- Use password in VNC
- Use updated svncterm 1.5-2
- Create ubuntu package for lxdone releases
- Create ubuntu package for custom context
- Snapshots
- Bandwidth limitation
- LVM storage backend
- Migration
- HDD Hotplug
- Use Ceph with LXD future native support
- Code migration to Python 3