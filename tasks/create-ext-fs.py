import os
from joblib import Task, TaskResult
from partlib import PartitionBuilder

class CreateExtFSTask(Task):
	description = "Create ext FS"
	stage = "test"

	provides = ['filesystem']

	def run(self):
		if os.system("mkfs.%s %s" % (self.job.attributes['fs-type'], PartitionBuilder.get_testpart())) != 0:
			return TaskResult.FAILED

		try:
			os.mkdir("/tank")
		except OSError:
			pass

		if os.system("mount %s /tank" % (PartitionBuilder.get_testpart())) != 0:
			return TaskResult.FAILED

		return TaskResult.PASSED

	def should_run(self):
		return (self.job.attributes['fs-type'] in ['ext2', 'ext3', 'ext4'])

CreateExtFSTask.register()
