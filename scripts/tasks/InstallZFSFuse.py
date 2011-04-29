from tasklib import Task

class InstallZFSFuseTask(Task):
	description = "zfs-fuse installation"
	stage = "test"

	provides = ['zfs']

	def run(self):
		if Dispatcher.get_input('fs_type') != 'zfs-fuse':
			return Task.SKIPPED

		if os.system("aptitude install -y zfs-fuse") != 0:
			return Task.FAILED

		return Task.PASSED

InstallZFSFuseTask.register()
