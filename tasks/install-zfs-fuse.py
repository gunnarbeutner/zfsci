from tasklib import Task, JobConfig

class InstallZFSFuseTask(Task):
	description = "zfs-fuse installation"
	stage = "test"

	provides = ['zfs']

	def run(self):
		if JobConfig.get_input('fs_type') != 'zfs-fuse':
			return Task.SKIPPED

		if os.system("aptitude install -y zfs-fuse") != 0:
			return Task.FAILED

		return Task.PASSED

InstallZFSFuseTask.register()
