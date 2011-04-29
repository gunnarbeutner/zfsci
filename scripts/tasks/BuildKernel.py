import os
import glob
from tasklib import Task

class BuildKernelTask(Task):
	description = "Build Linux kernel"
	stage = "test"

	dependencies = ['kernel-source']

	def prepare(self):
		os.chdir("/tank")

		for dir in glob.glob("linux-*"):
			os.chdir(dir)
			break

		if os.system("make mrproper") != 0:
			return Task.FAILED

		if os.system("make allyesconfig") != 0:
			return Task.FAILED

		if os.system("make -j 4") != 0:
			return Task.FAILED

		return Task.PASSED

	def run(self):
		if os.system("make -j 4") != 0:
			return Task.FAILED

		return Task.PASSED

BuildKernelTask.register()
