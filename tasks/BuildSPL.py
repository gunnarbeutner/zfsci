import os
from tasklib import Task, Dispatcher

class BuildSPLTask(Task):
	description = "Build SPL"
	stage = "test"

	dependencies = ['zfs-builddeps']
	provides = ['spl']

	def prepare(self):
		if Dispatcher.get_input('fs_type') != 'zfs':
			return Task.SKIPPED

		try:
			os.mkdir("/root/build")
		except OSError:
			pass

		os.chdir("/root/build")
		os.system("rm -Rf /root/build/spl")

	def run(self):
		if os.system("git clone git://github.com/behlendorf/spl.git spl") != 0:
			return Task.FAILED

		os.chdir("spl")

		if os.system("./configure --prefix=/usr") != 0:
			return Task.FAILED

		if os.system("make -j 4") != 0:
			return Task.FAILED

		if os.system("make install") != 0:
			return Task.FAILED

		return Task.PASSED

BuildSPLTask.register()
