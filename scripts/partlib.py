import sys
import os
from tasklib import Utility, JobConfig

class PartitionBuilder(object):
	_config = Utility.get_zfsci_config()

	@staticmethod
	def get_install_device():
		return PartitionBuilder._config['install_device']

	@staticmethod
	def get_rootpart():
		return PartitionBuilder.get_install_device() + '1'

	@staticmethod
	def get_swappart():
		return PartitionBuilder.get_install_device() + '2'

	@staticmethod
	def get_testpart():
		return PartitionBuilder.get_install_device() + '3'

	@staticmethod
	def setup_partitions():
		install_device = PartitionBuilder.get_install_device()

		if os.system("dd if=/dev/zero of=%s bs=512 count=1" % (install_device)) != 0:
			raise Error("Could not erase old partition table.")

		if os.system("parted --script -- %s mktable msdos" % (install_device)) != 0:
			raise Error("Could not create new partition table.")

		rootpart = PartitionBuilder.get_rootpart()
		JobConfig.set_input('rootpart', rootpart)
		if os.system("parted --script -- %s mkpart primary ext2 1M 10G" % (install_device)) != 0:
			raise Error("Could not create new / partition.")

		swappart = PartitionBuilder.get_swappart()
		JobConfig.set_input('swappart', swappart)
		if os.system("parted --script -- %s mkpart primary linux-swap 10G 14G" % (install_device)) != 0:
			raise Error("Could not create new swap partition.")

		testpart = PartitionBuilder.get_testpart()
		JobConfig.set_input('testpart', testpart)
		if os.system("parted --script -- %s mkpart primary sun-ufs 14G -1s" % (install_device)) != 0:
			raise Error("Could not create new test partition.")

		JobConfig.save()

		if os.system("mke2fs -j -m 0 -L / -I 128 %s" % (rootpart)) != 0:
			raise Error("Create not create new / filesystem.")

		if os.system("mkswap %s" % (swappart)) != 0:
			raise Error("Could not create new swap filesystem.")

	@staticmethod
	def mount_partitions():
		if os.system("mount -o remount,rw /mnt") != 0:
			try:
				os.makedirs("/mnt")
			except OSError:
				pass

			if os.system("mount %s /mnt" % (PartitionBuilder.get_rootpart())) != 0:
				raise Error("Could not mount node filesystem.")

		if os.system("mountpoint -q /mnt/dev") != 0:
			try:
				os.makedirs("/mnt/dev")
			except OSError:
				pass

			if os.system("mount --bind /dev /mnt/dev") != 0:
				raise Error("Could not mount /mnt/dev")

		if os.system("mountpoint -q /mnt/sys") != 0:
			try:
				os.makedirs("/mnt/sys")
			except OSError:
				pass

			if os.system("mount --bind /sys /mnt/sys") != 0:
				raise Error("Could not mount /mnt/sys")

		if os.system("mountpoint -q /mnt/proc") != 0:
			try:
				os.makedirs("/mnt/proc")
			except OSError:
				pass

			if os.system("mount -t proc none /mnt/proc") != 0:
				raise Error("Could not mount /mnt/proc")

		if os.system("mountpoint -q /mnt/var/lib/zfsci-data") != 0:
			try:
				os.makedirs("/mnt/var/lib/zfsci-data")
			except OSError:
				pass

			if os.system("mount --bind /var/lib/zfsci-data /mnt/var/lib/zfsci-data") != 0:
				raise Error("Could not mount /mnt/var/lib/zfsci-data")

	@staticmethod
	def unmount_partitions():
		os.system("umount /mnt/var/lib/zfsci-data /mnt/dev /mnt/sys /mnt/proc /mnt")

