import os
from joblib import Task, TaskResult
from partlib import PartitionBuilder

class CreateZPoolTask(Task):
	description = "Create zpool"
	stage = "test"

	dependencies = ['zfs']
	provides = ['filesystem']

	def run(self):
		if os.system("zpool create -f tank %s" % (PartitionBuilder.get_testpart())) != 0:
			return TaskResult.FAILED

		return TaskResult.PASSED

	def should_run(self):
		return (self.job.attributes['fs-type'] in ['zfs', 'zfs-fuse'])

CreateZPoolTask.register()
