import os
from tasklib import Task, Utility, JobConfig

class BuildSPLTask(Task):
	description = "Build SPL"
	stage = "test"

	dependencies = ['zfs-builddeps']
	provides = ['spl']

	def prepare(self):
		if JobConfig.get_input('fs-type') != 'zfs':
			return Task.SKIPPED

		try:
			os.mkdir("/root/build")
		except OSError:
			pass

		os.chdir("/root/build")
		os.system("rm -Rf spl")

		gitrepo = JobConfig.get_input('zfs-git-repo')
		gitcommit = JobConfig.get_input('zfs-git-commit')

		repodir = "%s/repositories/%s" % (Utility.get_persistent_dir(), gitrepo['spl'])
		if os.system("git clone %s spl" % (repodir)) != 0:
			return Task.FAILED

		os.chdir("spl")

		if os.system("git reset --hard `git rev-list --max-count=1 --before=%s %s`" % (gitcommit, gitrepo['branch'])) != 0:
			return Task.FAILED

		return Task.PASSED

	def run(self):
		if os.system("./configure --prefix=/usr") != 0:
			return Task.FAILED

		if os.system("make -j 4") != 0:
			return Task.FAILED

		if os.system("make install") != 0:
			return Task.FAILED

		return Task.PASSED

BuildSPLTask.register()
