#Virtual Appliance Creation
LXD native images are basically compressed files. OpenNebula uses block based images in its default operation mode. The default LXD images will NOT work with **LXDoNe**. This guide is meant for converting a LXD image into a OpenNebula-ready LXD image.

## Create a default container

```
lxc launch images:16.04 lxdone
```

Now you should have a container named **lxdone** running. To check the container state: 

```
lxc list
```

The output should be like this:

```
+---------+---------+---------------------+------+------------+-----------+
|  NAME   |  STATE  |        IPV4         | IPV6 |    TYPE    | SNAPSHOTS |
+---------+---------+---------------------+------+------------+-----------+
| lxdone  | RUNNING |                     |      | PERSISTENT | 0         |
+---------+---------+---------------------+------+------------+-----------+
```

LXD default profiles attaches a NIC to every new container. This behaviour must be removed for a lxd-node controlled by OpenNebula. If you did this in the [setup guide](Setup.md) then attach a NIC by: 

```
lxc config device add lxdone eth0 nic nictype=bridged parent=br0
```

Enter the container as root.

```
lxc exec lxdone bash 
root@lxdone:
```

## Container tweaking:
Customize your container all you want

```
root@lxdone: apt install one-context
root@lxdone: passwd 
......
......
root@lxdone: exit
```

### OpenNebula contextualization
Follow [KVM contextualization](link). Then install curl and openssh-server for ssh contextualization.

```
root@lxdone: apt install openssh-server curl
```

Replace 

```
get_interface_mac()
{
    ip link show | awk '/^[0-9]+: [A-Za-z0-9]+:/ { device=$2; gsub(/:/, "",device)} /link\/ether/ { print device " " $2 }'
}
```

by 

```
get_interface_mac()
{
    ip link show | awk '/^[0-9]+: [A-Za-z0-9@]+:/ { device=$2; gsub(/:/, "",device); split(device,dev,"\@")} /link\/ether/ { print dev[1]  " " $2 }'
}
```

in **/etc/one-context.d/10-network** and add 

```
    elif [ -f /mnt/context.sh ]; then
        cp /mnt/context.sh ${CONTEXT_NEW}
```

before ```elif vmware_context ; then``` in **/usr/sbin/one-contextd**

### Tips
- When using *sudo* as a non-root user inside a container you will likely receive *sudo: no tty present and no askpass program specified*. When appending -S to sudo this gets fixed. It would be a good idea to create an alias.
- using *su* behaves abnormally too, but the fix for this is not that comfortable. You can find info about this [here](<!-- link a stgraber + dann1 -->)
- This strange behaviour occurs when entering by *lxc exec*, when you log by ssh things work normal.
- When login occurs via svncterm (which is the same as *lxc exec*), entering backspace key prints *^H* instead of deleting the last character. Replace *ERASECHAR       0177* by *ERASECHAR       010* in **/etc/login.defs** to correct this. Ctrl+U keybinding deletes the whole line in the login prompt.

### Modify LXD-metadata
In order to populate **/etc/hosts** and **/etc/hostname** inside the container managed by OpenNebula. We'll need to modify container metadata.

Replace 

```
        "/etc/hostname": {
            "template": "hostname.tpl",
            "when": [
                "create",
                "copy"
            ]
        },
        "/etc/hosts": {
            "template": "hosts.tpl",
            "when": [
                "create",
                "copy"
            ]
```

by 

```
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
```

in **/var/lib/lxd/lxdone/metadata.yaml**

Force custom hooks

```
echo "{{ config_get("user.hostname", "lxdone")}}" > /var/lib/lxd/lxdone/templates/hostname.tpl
sudo sed -i 's/127.0.1.1   {{ container.name }}/127.0.1.1   {{ config_get("user.hostname", "lxdone")}}/' /var/lib/lxd/lxdone/templates/hosts.tpl
```

## Dump container into raw image

Check how much space your container needs.

```
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

```
sudo umount $loop
sudo losetup -d $loop
```

Optionally compress your image. This is useful if you copy it to **/var/tmp/** in the frontend, then extract it there and upload via "Path in OpenNebula server" in the image upload section on Sunstone.

```
tar cvJpf lxdone-custom.tar.xz lxdone.img
```