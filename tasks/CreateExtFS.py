import os
from tasklib import Task

class CreateExtFSTask(Task):
	description = "Create ext FS"
	stage = "test"

	provides = ['filesystem']

	def run(self):
		fs_type = Dispatcher.get_input('fs-type')

		if not fs_type in ['ext2', 'ext3', 'ext4']:
			return Task.SKIPPED

		if os.system("mkfs.%s /dev/sda3" % (fs_type)) != 0:
			return Task.FAILED

		try:
			os.mkdir("/tank")
		except OSError:
			pass

		if os.system("mount /dev/sda3 /tank") != 0:
			return Task.FAILED

		return Task.PASSED

CreateExtFSTask.register()
