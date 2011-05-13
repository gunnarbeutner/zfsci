from joblib import Task, TaskResult

class ZFSDepsOpenSUSETask(Task):
	description = "ZFS dependencies installation"
	stage = "test"

	provides = ['zfs-builddeps']

	def run(self):
		if os.system("zypper install -y git-core zlib-devel libuuid-devel") != 0:
			return TaskResult.FAILED

		return TaskResult.PASSED

	def should_run(self):
		return (self.job.attributes['fs-type'] == 'zfs' and self.job.attributes['distribution'] == 'opensuse')

ZFSDepsOpenSUSETask.register()
