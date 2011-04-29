from tasklib import Task

class InstallBuildUtilsTask(Task):
	description = "Build utilities installation"
	stage = "build"

	def run(self):
		if os.system("aptitude install -y build-essential git-core") != 0:
			return Task.FAILED

		return Task.PASSED

InstallBuildUtilsTask.register()
