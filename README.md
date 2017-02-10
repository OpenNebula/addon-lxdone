# Addon LXDoNe

<a href="https://github.com/OpenNebula/addon-lxdone"><img src="picts/LXDoNe-logo-final.png" align="left" hspace="10" vspace="6"></a>

<br />

[![lxdone](https://img.shields.io/badge/release-1702-3c97f3.svg?style=flat-square)](https://linuxcontainers.org/lxd/)

[![LXD](https://img.shields.io/badge/lxd-LTS-orange.svg?style=flat-square)](https://linuxcontainers.org/lxd/)
[![Ceph](https://img.shields.io/badge/ceph-LTS-red.svg?style=flat-square)](https://ceph.com)
[![OpenNebula](https://img.shields.io/badge/one-5.2.1-blue.svg?style=flat-square)](https://opennebula.org)

[![pylxd](https://img.shields.io/badge/pylxd-2.0.5-brightgreen.svg?style=flat-square)](https://pylxd.readthedocs.io/en/stable/)
[![VNC](https://img.shields.io/badge/VNC-svncterm-yellow.svg?style=flat-square)](https://pylxd.readthedocs.io/en/stable/)

[![tweet](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)](https://img.shields.io/twitter/url/http/shields.io.svg?style=social)

<br />
# Introduction
**LXDoNe** is an addon for OpenNebula to manage **LXD** Containers. It fits in the Virtualization and Monitorization Driver section according to OpenNebula's Architecture. It uses the **pylxd** API for several container tasks. This addon is the continuation of [LXCoNe](https://github.com/OpenNebula/addon-lxcone/), an addon for **LXC**.

# Introduction

**LXDoNe** is an addon for OpenNebula to manage **LXD** Containers. It fits in the Virtualization and Monitorization Driver section according to OpenNebula's Architecture. It uses the **pylxd** API for several container tasks. This addon is the continuation of [LXCoNe](https://github.com/OpenNebula/addon-lxcone/), an addon for **LXC**.

[LXD](https://linuxcontainers.org/lxd/) is a daemon which provides a REST API to drive **LXC** containers. Containers are lightweight OS-level Virtualization instances, they behave like Virtual Machines but don't suffer from hardware emulation processing penalties by sharing the kernel with the host. They run bare-metal-like, simple containers can boot up in 2 seconds consuming less than 32MB of RAM and a minimal fraction of a CPU Core. Check out this [performance comparison against KVM](https://insights.ubuntu.com/2015/05/18/lxd-crushes-kvm-in-density-and-speed/) if you don't know much about LXD.

# Releases && Features  

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
- VNC (Work in progress)
- Specify target device for extra disks
- Contextualization compatibility
- 802.1Q network driver compatibility

# TODO
- Migration
- Snapshots
- LVM storage backend
- Hot-attach/detach NICs and HDD
- Bandwidth limitation

# Known Bugs
- [ ]  VNC - The first container in a virtualization node is the only one who gets graphic session.

# Compatibility
**LXDoNe** is not an update of **LXCoNe** so your old containers won't be manageable out of the box, but you can  adapt them to the new image format, read [Virtual Appliance](Image.md). 

# Setup
Check the [Setup Guide](Setup.md)  to deploy a working scenario.
Also there are some Ansible scripts for automatic deployment.

# Contributing
If you want to contribute feel free to request new features, the TODO list is stated according to our priority order. Check the [Flowchart](https://github.com/OpenNebula/addon-lxdone/tree/master/flow_chart) to get a bettter understanding of the driver internals, pictures starting with **one-**    ex. [one-deploy.png](https://github.com/OpenNebula/addon-lxdone/tree/master/flow_chart/one-deploy.png) ressemble the scripts overview. 

# Developers
- **Sergio Vega Gutiérrez** (sergiojvg92@gmail.com)
- **José Manuel de la Fé Herrero** (jmdelafe92@gmail.com)
- **Daniel Clavijo Coca** (dann1telecom@gmail.com)
