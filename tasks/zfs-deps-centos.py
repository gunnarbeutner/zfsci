from tasklib import Task, JobConfig

class ZFSDepsCentOSTask(Task):
	description = "ZFS dependencies installation"
	stage = "test"

	provides = ['zfs-builddeps']

	def run(self):
		if JobConfig.get_input('fs-type') != 'zfs' or JobConfig.get_input('distribution') != 'centos':
			return Task.SKIPPED

		if os.system("yum install -y git-core zlib-devel e2fsprogs-devel") != 0:
			return Task.FAILED

		return Task.PASSED

ZFSDepsCentOSTask.register()
