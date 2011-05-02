import os
import glob
from tasklib import Task

class BuildKernelTask(Task):
	description = "Build Linux kernel"
	stage = "test"

	dependencies = ['filesystem']

	KERNEL_URL = "http://www.de.kernel.org/pub/linux/kernel/v2.6/linux-2.6.38.tar.gz"

	def prepare(self):
		# TODO: remove this
		return Task.SKIPPED

		os.chdir("/tank")

		if os.system("wget -O - %s | tar xz" % (BuildKernelTask.KERNEL_URL)) != 0:
			return Task.FAILED

		for dir in glob.glob("linux-*"):
			os.chdir(dir)
			break

		if os.system("make mrproper") != 0:
			return Task.FAILED

		if os.system("make allyesconfig") != 0:
			return Task.FAILED

		return Task.PASSED

	def run(self):
		if os.system("make -j 4") != 0:
			return Task.FAILED

		return Task.PASSED

BuildKernelTask.register()
