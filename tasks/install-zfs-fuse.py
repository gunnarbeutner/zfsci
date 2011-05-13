from joblib import Task, TaskResult

class InstallZFSFuseTask(Task):
	description = "zfs-fuse installation"
	stage = "test"

	provides = ['zfs']

	def run(self):
		if os.system("aptitude install -y zfs-fuse") != 0:
			return TaskResult.FAILED

		return TaskResult.PASSED

	def should_run(self):
		return (self.job.attributes['fs-type'] == 'zfs-fuse')

InstallZFSFuseTask.register()
