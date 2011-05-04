from tasklib import Task, JobConfig

class ZFSDepsOpenSUSETask(Task):
	description = "ZFS dependencies installation"
	stage = "test"

	provides = ['zfs-builddeps']

	def run(self):
		if JobConfig.get_input('fs-type') != 'zfs' or JobConfig.get_input('distribution') != 'opensuse':
			return Task.SKIPPED

		if os.system("zypper install -y git-core zlib-devel libuuid-devel") != 0:
			return Task.FAILED

		return Task.PASSED

ZFSDepsOpenSUSETask.register()
