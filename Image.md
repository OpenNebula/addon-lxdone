

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

Customize your container all you want

```bash
root@lxdone: apt install one-context
root@lxdone: passwd
......
......
root@lxdone: exit
```


<a id="markdown-opennebula-contextualization" name="opennebula-contextualization"></a>
### OpenNebula contextualization ###

Follow [KVM contextualization](https://docs.opennebula.org/5.4/operation/vm_setup/kvm.html). Then install curl and openssh-server for ssh contextualization.

```bash
root@lxdone: apt install openssh-server curl
```

In **/etc/one-context.d/10-network** replace _get_interface_mac_ function

```bash
get_interface_mac()
{
    ip link show | awk '/^[0-9]+: [A-Za-z0-9]+:/ { device=$2; gsub(/:/, "",device)} /link\/ether/ { print device " " $2 }'
}
```

by

```bash
get_interface_mac()
{
    ip link show | awk '/^[0-9]+: [A-Za-z0-9@]+:/ { device=$2; gsub(/:/, "",device); split(device,dev,"\@")} /link\/ether/ { print dev[1]  " " $2 }'
}
```

and, in **/usr/sbin/one-contextd**, add

```bash
    elif [ -f /mnt/context.sh ]; then       #LXDoNe
        cp /mnt/context.sh ${CONTEXT_NEW}   #LXDoNe
```

inside _get_new_context_ function, before ```elif vmware_context ; then```. Should look like this:

```bash
    function get_new_context {
    CONTEXT_DEV=`blkid -l -t LABEL="CONTEXT" -o device`
    if [ -e "$CONTEXT_DEV" ]; then
        mount -t iso9660 -L CONTEXT -o ro /mnt
        if [ -f /mnt/context.sh ]; then
            cp /mnt/context.sh ${CONTEXT_NEW}
        fi

        echo "umount /mnt" > ${END_CONTEXT}
    elif [ -f /mnt/context.sh ]; then       #LXDoNe
        cp /mnt/context.sh ${CONTEXT_NEW}   #LXDoNe
    elif vmware_context ; then
        vmtoolsd --cmd 'info-get guestinfo.opennebula.context' | \
            openssl base64 -d > ${CONTEXT_NEW}
    elif curl -o ${CONTEXT_NEW} http://169.254.169.254/latest/user-data ; then
        echo -n ""
    fi
}
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
sudo cp -rpa sudo du -sh /var/lib/lxd/containers/lxdone/* /mnt/
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