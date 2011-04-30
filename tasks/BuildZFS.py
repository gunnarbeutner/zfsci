import os
from tasklib import Task

class BuildZFSTask(Task):
	description = "ZFS build"
	stage = "test"

	dependencies = ['zfs-builddeps', 'spl']
	provides = ['zfs']

	def prepare(self):
		if Dispatcher.get_input('fs_type') != 'zfs':
			return Task.SKIPPED

		try:
			os.mkdir("/root/build")
		except OSError:
			pass

		os.chdir("/root/build")
		os.system("rm -Rf /root/build/zfs")

	def run(self):
		if os.system("git clone git://github.com/behlendorf/zfs.git zfs") != 0:
			return Task.FAILED

		os.chdir("zfs")

		if os.system("./configure --prefix=/usr") != 0:
			return Task.FAILED

		if os.system("make -j 4") != 0:
			return Task.FAILED

		if os.system("make install") != 0:
			return Task.FAILED

		return Task.PASSED

BuildZFSTask.register()
