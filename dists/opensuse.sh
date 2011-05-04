#!/bin/sh
if ! cd `dirname $0`; then
	echo "Could not cd to jobs directory."
	exit 1
fi

if [ -z "$1" ]; then
	echo "Syntax: $0 <target-file>"
	exit 1
fi

BUILDDIR=/tmp/opensuse-fs
IMAGEFILE=$1

umount $BUILDDIR/dev $BUILDDIR/sys $BUILDDIR/proc >/dev/null 2>&1

rm -Rf $BUILDDIR

# install rinse
aptitude install -y rinse

# install base system
if ! rinse --directory $BUILDDIR --distribution opensuse-11.1 --arch amd64; then
	echo "rinse failed"
	exit 1
fi

# set up networking
cat > $BUILDDIR/etc/sysconfig/network/ifcfg-eth0 <<NETWORK
DEVICE=eth0
BOOTPROTO=dhcp
STARTMODE=auto
NETWORK

# disable cron
chroot $BUILDDIR chkconfig cron off

# mount dev/sys/proc
mount --bind /dev $BUILDDIR/dev
mount --bind /sys $BUILDDIR/sys
mount -t proc none $BUILDDIR/proc

# install additional packages
chroot $BUILDDIR zypper install -y python nfs-client kdump gcc make mkinitrd

# copy crash kernel and build initrd
CRASHKERNEL="vmlinuz-`uname -r`"
CRASHINITRD="initrd.img-`uname -r`"
CRASHCONFIG="config-`uname -r`"
mkdir $BUILDDIR/crashkernel
cp /boot/$CRASHKERNEL /boot/$CRASHINITRD /boot/$CRASHCONFIG $BUILDDIR/crashkernel
cp -a /lib/modules/`uname -r` $BUILDDIR/lib/modules

mkdir -p $BUILDDIR/var/crash

#cat >> $BUILDDIR/etc/default/kdump-tools <<KDUMP
#USE_KDUMP=1
#KDUMP_SYSCTL="kernel.panic_on_oops=1"
#MAKEDUMP_ARGS="-c -d 31"
#
#KDUMP_KERNEL="/crashkernel/$CRASHKERNEL"
#KDUMP_INITRD="/crashkernel/$CRASHINITRD"
#KDUMP

#cat >> $BUILDDIR/etc/default/kexec <<KEXEC
#LOAD_KEXEC=false
#KEXEC

# clean up package archive
chroot $BUILDDIR zypper clean

# umount dev/sys/proc
umount $BUILDDIR/dev $BUILDDIR/sys $BUILDDIR/proc

# remove udev rules
rm -f $BUILDDIR/etc/udev/rules.d/*persistent*

# set up rc.local script
cat > $BUILDDIR/etc/init.d/rc-local <<BOOTLOCAL
#!/bin/sh
### BEGIN INIT INFO
# Provides: rc-local
# Required-Start: \$remote_fs
# Required-Stop: \$remote_fs
# Default-Start: 3 5
# Default-Stop: 0 1 2 6
# Description: rc.local
### END INIT INFO

exec sh -c /etc/rc.local
BOOTLOCAL

chmod +x $BUILDDIR/etc/init.d/rc-local

chroot $BUILDDIR chkconfig --add rc-local

tar cfzC /tmp/opensuse.tar.gz $BUILDDIR .
mv /tmp/opensuse.tar.gz $IMAGEFILE

exit 0
