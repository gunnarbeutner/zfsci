from tasklib import Task, JobConfig

class ZFSDepDebianTask(Task):
	description = "ZFS dependencies installation"
	stage = "test"

	provides = ['zfs-builddeps']

	def run(self):
		if JobConfig.get_input('fs-type') != 'zfs' or JobConfig.get_input('distribution') != 'debian':
			return Task.SKIPPED

		if os.system("aptitude install -y git-core module-assistant uuid-dev zlib1g-dev gawk") != 0:
			return Task.FAILED

		return Task.PASSED

ZFSDepDebianTask.register()
