

<a id="markdown-virtual-appliance-creation" name="virtual-appliance-creation"></a>
# Virtual Appliance Creation #

LXD native images are basically compressed files. OpenNebula uses block based images in its default operation mode. The default LXD images will NOT work with **LXDoNe**. This guide is meant for converting a LXD image into a OpenNebula-ready LXD image.

<!-- TOC -->

- [Virtual Appliance Creation](#virtual-appliance-creation)
    - [Create a default container](#create-a-default-container)
    - [Container tweaking](#container-tweaking)
        - [OpenNebula contextualization](#opennebula-contextualization)
        - [Tips](#tips)
    - [Dump container into raw image](#dump-container-into-raw-image)

<!-- /TOC -->


<a id="markdown-create-a-default-container" name="create-a-default-container"></a>
## Create a default container ##

```bash
lxc launch images:16.04 lxdone
```

Now you should have a container named **lxdone** running. To check the container state:

```bash
lxc list
```

The output should be like this:

```plain
+---------+---------+---------------------+------+------------+-----------+
|  NAME   |  STATE  |        IPV4         | IPV6 |    TYPE    | SNAPSHOTS |
+---------+---------+---------------------+------+------------+-----------+
| lxdone  | RUNNING |                     |      | PERSISTENT | 0         |
+---------+---------+---------------------+------+------------+-----------+
```

LXD default profiles attaches a NIC to every new container. This behaviour must be removed for a lxd-node controlled by OpenNebula. If you did this in the [setup guide](Setup.md) then attach a NIC by:

```bash
lxc config device add lxdone eth0 nic nictype=bridged parent=br0
```

Enter the container as root.

```bash
lxc exec lxdone bash
root@lxdone:
```


<a id="markdown-container-tweaking" name="container-tweaking"></a>
## Container tweaking ##

Customize your container all you want. You can configure the previous NIC now.

```bash
root@lxdone: apt install bunch-of-stuff
root@lxdone: passwd
......
......
root@lxdone: exit
```


<a id="markdown-opennebula-contextualization" name="opennebula-contextualization"></a>
### OpenNebula contextualization ###

Install [addon-context-linux-lxd](https://github.com/cloxcloud/addon-context-linux-lxd/). This is our modified version of OpenNebula contextualization package.

```bash
 context=one-context-lxd_5.4.2-1.deb
 wget https://github.com/cloxcloud/addon-context-linux-lxd/releases/download/v5.4.2/$context && dpkg -i $context
```

<a id="markdown-tips" name="tips"></a>
### Tips ###

- When using *sudo* as a non-root user inside a container you will likely receive *sudo: no tty present and no askpass program specified*. When appending -S to sudo this gets fixed. It would be a good idea to create an alias.
- using *su* behaves abnormally too, but the fix for this is not that comfortable. Refer to [this lxd issue](https://github.com/lxc/lxd/issues/3218). This strange behaviour occurs when entering by *lxc exec*, when you log by ssh things work normal.
- When login occurs via svncterm (which is the same as *lxc exec*), entering backspace key prints *^H* instead of deleting the last character. Replace *ERASECHAR       0177* by *ERASECHAR       010* in **/etc/login.defs** to correct this. Ctrl+U keybinding deletes the whole line in the login prompt.

<a id="markdown-dump-container-into-raw-image" name="dump-container-into-raw-image"></a>
## Dump container into raw image ##

Check how much space your container needs.

```bash
sudo du -sh /var/lib/lxd/containers/lxdone/
```

Push container into block device. You may change the 1G size. The minimum required is a little bigger than the previous output.

```bash
lxc stop lxdone
truncate -s 1G /var/tmp/lxdone.img
loop=$(sudo losetup --find --show /var/tmp/lxdone.img)
sudo mkfs.ext4 $loop
sudo mount $loop /mnt/
sudo cp -rpa /var/lib/lxd/containers/lxdone/* /mnt/
```

Make sure there were no errors regarding space in the previous output.

```bash
sudo umount $loop
sudo losetup -d $loop
```

Optionally compress your image. This is useful if you copy it to **/var/tmp/** in the frontend, extract it there and upload via "Path in OpenNebula server" in the image upload section in Sunstone.

```bash
tar cvJpf lxdone-custom.tar.xz lxdone.img
```
