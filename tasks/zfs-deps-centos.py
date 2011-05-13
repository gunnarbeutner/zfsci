from joblib import Task, TaskResult

class ZFSDepsCentOSTask(Task):
	description = "ZFS dependencies installation"
	stage = "test"

	provides = ['zfs-builddeps']

	def run(self):
		if os.system("yum install -y git-core zlib-devel e2fsprogs-devel") != 0:
			return TaskResult.FAILED

		return TaskResult.PASSED

	def should_run(self):
		return (self.job.attributes['fs-type'] == 'zfs' and self.job.attributes['distribution'] == 'centos')

ZFSDepsCentOSTask.register()
