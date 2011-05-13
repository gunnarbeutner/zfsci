import os
from joblib import Task, TaskResult
from tasklib import Utility

class BuildSPLTask(Task):
	description = "Build SPL"
	stage = "test"

	dependencies = ['zfs-builddeps']
	provides = ['spl']

	def prepare(self):
		try:
			os.mkdir("/root/build")
		except OSError:
			pass

		os.chdir("/root/build")
		os.system("rm -Rf spl")

		gitinfo = self.job.attributes['zfs-git-repo']

		repodir = "%s/repositories/%s" % (Utility.get_persistent_dir(), gitinfo['spl-repository'])
		if os.system("git clone -b %s %s spl" % (gitinfo['spl-branch'], repodir)) != 0:
			return TaskResult.FAILED

		os.chdir("spl")

		if os.system("git reset --hard `git rev-list --max-count=1 --before=%s HEAD`" % (gitinfo['timestamp'])) != 0:
			return TaskResult.FAILED

		return TaskResult.PASSED

	def run(self):
		if os.system("./configure --prefix=/usr") != 0:
			return TaskResult.FAILED

		if os.system("make -j 8") != 0:
			return TaskResult.FAILED

		if os.system("make install") != 0:
			return TaskResult.FAILED

		if os.system("modprobe spl") != 0:
			return TaskResult.FAILED

		return TaskResult.PASSED

	def should_run(self):
		return (self.job.attributes['fs-type'] == 'zfs')


BuildSPLTask.register()
