from joblib import Task, TaskResult

class ZFSDepDebianTask(Task):
	description = "ZFS dependencies installation"
	stage = "test"

	provides = ['zfs-builddeps']

	def run(self):
		if os.system("aptitude install -y git-core module-assistant uuid-dev zlib1g-dev gawk") != 0:
			return TaskResult.FAILED

		return TaskResult.PASSED

	def should_run(self):
		return (self.job.attributes['fs-type'] == 'zfs' and self.job.attributes['distribution'] == 'debian')

ZFSDepDebianTask.register()
