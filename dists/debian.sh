#!/bin/sh
if ! cd `dirname $0`; then
	echo "Could not cd to jobs directory."
	exit 1
fi

. ../zfsci.conf

if [ -z "$1" ]; then
	echo "Syntax: $0 <target-file>"
	exit 1
fi

BUILDDIR=/tmp/debian-fs
IMAGEFILE=$1

umount $BUILDDIR/dev $BUILDDIR/sys $BUILDDIR/proc >/dev/null 2>&1

rm -Rf $BUILDDIR

# disable init scripts in the build environment
mkdir -p $BUILDDIR/usr/sbin
cat > $BUILDDIR/usr/sbin/policy-rc.d <<POLICYRCD
#!/bin/sh
exit 101
POLICYRCD
chmod +x $BUILDDIR/usr/sbin/policy-rc.d

# install base system
if ! debootstrap squeeze $BUILDDIR $DEBIAN_MIRROR; then
	echo "debootstrap failed"
	exit 1
fi

# set up networking
cat > $BUILDDIR/etc/network/interfaces <<INTERFACES
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
INTERFACES

# disable cron
chroot $BUILDDIR update-rc.d -f cron remove

# mount dev/sys/proc
mount --bind /dev $BUILDDIR/dev
mount --bind /sys $BUILDDIR/sys
mount -t proc none $BUILDDIR/proc


# update package list
chroot $BUILDDIR aptitude update

# install additional packages
chroot $BUILDDIR aptitude install -y python nfs-client \
	kdump-tools file initramfs-tools build-essential

# copy crash kernel and build initrd
CRASHKERNEL="vmlinuz-`uname -r`"
CRASHINITRD="initrd.img-`uname -r`"
CRASHCONFIG="config-`uname -r`"
cp /boot/$CRASHKERNEL /boot/$CRASHCONFIG $BUILDDIR/boot
cp -a /lib/modules/`uname -r` $BUILDDIR/lib/modules
chroot $BUILDDIR update-initramfs -c -k `uname -r`
mkdir $BUILDDIR/crashkernel
mv $BUILDDIR/boot/$CRASHKERNEL $BUILDDIR/boot/$CRASHINITRD \
	$BUILDDIR/boot/$CRASHCONFIG $BUILDDIR/crashkernel

mkdir -p $BUILDDIR/var/crash

cat >> $BUILDDIR/etc/default/kdump-tools <<KDUMP
USE_KDUMP=1
KDUMP_SYSCTL="kernel.panic_on_oops=1"
MAKEDUMP_ARGS="-c -d 31"

KDUMP_KERNEL="/crashkernel/$CRASHKERNEL"
KDUMP_INITRD="/crashkernel/$CRASHINITRD"
KDUMP

cat >> $BUILDDIR/etc/default/kexec <<KEXEC
LOAD_KEXEC=false
KEXEC

# clean up temporary files
chroot $BUILDDIR aptitude clean

# umount dev/sys/proc
umount $BUILDDIR/dev $BUILDDIR/sys $BUILDDIR/proc

# remove policy script
rm -f $BUILDDIR/usr/sbin/policy-rc.d

# remove udev rules
rm -f $BUILDDIR/etc/udev/rules.d/*persistent*

tar cfzC /tmp/debian.tar.gz $BUILDDIR .
mv /tmp/debian.tar.gz $IMAGEFILE

exit 0
