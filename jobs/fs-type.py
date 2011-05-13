from tasklib import Attribute

class FSTypeAttribute(Attribute):
	name = "fs-type"
	description = "Filesystem type"

	def get_values(self):
		return ['zfs', 'zfs-fuse', 'ext2', 'ext3', 'ext4']

FSTypeAttribute.register()
