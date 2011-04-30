import os
import glob
from tasklib import Task

class InstallKernelTask(Task):
	description = "Linux kernel installation"
	stage = "build"

	def run(self):
		if os.system("aptitude install -y linux-image-amd64") != 0:
			return Task.FAILED

		return Task.PASSED

InstallKernelTask.register()
