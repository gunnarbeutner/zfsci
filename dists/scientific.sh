#!/bin/sh
if ! cd `dirname $0`; then
	echo "Could not cd to jobs directory."
	exit 1
fi

if [ -z "$1" ]; then
	echo "Syntax: $0 <target-file>"
	exit 1
fi

BUILDDIR=/tmp/scientific-fs
IMAGEFILE=$1

umount $BUILDDIR/dev $BUILDDIR/sys $BUILDDIR/proc >/dev/null 2>&1

rm -Rf $BUILDDIR

# install rinse
aptitude install -y rinse

# install base system
if ! rinse --config ../misc/rinse/rinse.conf --pkgs-dir ../misc/rinse/ \
		--directory $BUILDDIR --distribution scientific-6 --arch amd64; then
	echo "rinse failed"
	exit 1
fi

# copy resolv.conf
cp /etc/resolv.conf $BUILDDIR/etc/

# set up networking
cat > $BUILDDIR/etc/sysconfig/network-scripts/ifcfg-eth0 <<NETWORK
DEVICE=eth0
BOOTPROTO=dhcp
ONBOOT=yes
NETWORK

cat > $BUILDDIR/etc/sysconfig/network <<NETWORK
NETWORKING=yes
HOSTNAME=zfsci-node
NETWORK

# disable cron
chroot $BUILDDIR chkconfig crond off

# mount dev/sys/proc
mount --bind /dev $BUILDDIR/dev
mount --bind /sys $BUILDDIR/sys
mount -t proc none $BUILDDIR/proc

# install epel repository
wget -O $BUILDDIR/epel-release-6-5.noarch.rpm http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-5.noarch.rpm
chroot $BUILDDIR rpm -i epel-release-6-5.noarch.rpm
rm -f $BUILDDIR/epel-release-6-5.noarch.rpm

# install additional packages
chroot $BUILDDIR yum install -y python26 nfs-utils crash gcc make wget

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

tar cfzC /tmp/scientific.tar.gz $BUILDDIR .
mv /tmp/scientific.tar.gz $IMAGEFILE

exit 0
