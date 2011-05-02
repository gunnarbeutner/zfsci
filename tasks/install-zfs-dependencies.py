from tasklib import Task

class InstallZFSDependenciesTask(Task):
	description = "ZFS dependencies installation"
	stage = "test"

	provides = ['zfs-builddeps']

	def run(self):
		if Dispatcher.get_input('fs-type') != 'zfs':
			return Task.SKIPPED

		if os.system("aptitude install -y module-assistant uuid-dev zlib1g-dev") != 0:
			return Task.FAILED

		if os.system("module-assistant prepare -i") != 0:
			return Task.FAILED

		return Task.PASSED

InstallZFSDependenciesTask.register()
