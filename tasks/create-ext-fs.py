import os
from tasklib import Task, JobConfig
from partlib import PartitionBuilder

class CreateExtFSTask(Task):
	description = "Create ext FS"
	stage = "test"

	provides = ['filesystem']

	def run(self):
		fs_type = JobConfig.get_input('fs-type')

		if not fs_type in ['ext2', 'ext3', 'ext4']:
			return Task.SKIPPED

		if os.system("mkfs.%s %s" % (fs_type, PartitionBuilder.get_testpart())) != 0:
			return Task.FAILED

		try:
			os.mkdir("/tank")
		except OSError:
			pass

		if os.system("mount %s /tank" % (PartitionBuilder.get_testpar())) != 0:
			return Task.FAILED

		return Task.PASSED

CreateExtFSTask.register()
