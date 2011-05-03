import os
from tasklib import Task, JobConfig
from partlib import PartitionBuilder

class CreateZPoolTask(Task):
	description = "Create zpool"
	stage = "test"

	dependencies = ['zfs']
	provides = ['filesystem']

	def run(self):
		fs_type = JobConfig.get_input('fs-type')

		if fs_type != 'zfs' and fs_type != 'zfs-fuse':
			return Task.SKIPPED

		if os.system("zpool create -f tank %s" % (PartitionBuilder.get_testpart())) != 0:
			return Task.FAILED

		return Task.PASSED

CreateZPoolTask.register()
