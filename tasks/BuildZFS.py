import os
from tasklib import Task, Dispatcher

class BuildZFSTask(Task):
	description = "Build ZFS"
	stage = "test"

	dependencies = ['zfs-builddeps', 'spl']
	provides = ['zfs']

	def prepare(self):
		if Dispatcher.get_input('fs-type') != 'zfs':
			return Task.SKIPPED

		try:
			os.mkdir("/root/build")
		except OSError:
			pass

		os.chdir("/root/build")
		os.system("rm -Rf /root/build/zfs")

	def run(self):
		(repository, branch, commit) = Dispatcher.get_input('zfs-gitinfo').split(' ', 2)

		repodir = "%s/%s" % (Dispatcher.get_persistent_dir(), repository)
		if os.system("git clone %s zfs" % (repodir) != 0:
			return Task.FAILED

		os.chdir("zfs")

		if os.system("git revert --hard %s" % (commit)) != 0:
			return Task.FAILED

		if os.system("./configure --prefix=/usr") != 0:
			return Task.FAILED

		if os.system("make -j 4") != 0:
			return Task.FAILED

		if os.system("make install") != 0:
			return Task.FAILED

		return Task.PASSED

BuildZFSTask.register()
