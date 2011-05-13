import sys
import os
from tasklib import Utility

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
		if os.system("parted --script -- %s mkpart primary ext2 1M 10G" % (install_device)) != 0:
			raise Error("Could not create new / partition.")

		swappart = PartitionBuilder.get_swappart()
		if os.system("parted --script -- %s mkpart primary linux-swap 10G 14G" % (install_device)) != 0:
			raise Error("Could not create new swap partition.")

		testpart = PartitionBuilder.get_testpart()
		if os.system("parted --script -- %s mkpart primary sun-ufs 14G -1s" % (install_device)) != 0:
			raise Error("Could not create new test partition.")

		if os.system("mke2fs -j -m 0 -L / -I 128 %s" % (rootpart)) != 0:
			raise Error("Create not create new / filesystem.")

		if os.system("mkswap %s" % (swappart)) != 0:
			raise Error("Could not create new swap filesystem.")

	@staticmethod
	def mount_partitions():
		if os.system("mountpoint -q /mnt") != 0 or os.system("mount -o remount,rw /mnt") != 0:
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

		persistent_dir = Utility.get_persistent_dir()
		if os.system("mountpoint -q /mnt/%s" % (persistent_dir)) != 0:
			try:
				os.makedirs("/mnt/%s" % (persistent_dir))
			except OSError:
				pass

			if os.system("mount --bind %s /mnt/%s" % (persistent_dir, persistent_dir)) != 0:
				raise Error("Could not mount /mnt/%s" % (persistent_dir))

	@staticmethod
	def unmount_partitions():
		persistent_dir = Utility.get_persistent_dir()
		os.system("umount /mnt/%s /mnt/dev /mnt/sys /mnt/proc /mnt" % (persistent_dir))

