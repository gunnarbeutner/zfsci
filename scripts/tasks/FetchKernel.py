import os
from tasklib import Task

class FetchKernelTask(Task):
	description = "Download Linux kernel"
	stage = "test"

	dependencies = ['filesystem']
	provides = ['kernel-source']

	KERNEL_URL = "http://www.de.kernel.org/pub/linux/kernel/v2.6/linux-2.6.38.tar.bz2"

	def prepare(self):
		os.system("aptitude install -y bzip2")

		os.chdir("/tank")

	def run(self):
		if os.system("wget -O - %s | tar xj" % (FetchKernelTask.KERNEL_URL)) != 0:
			return Task.FAILED

		return Task.PASSED

FetchKernelTask.register()
