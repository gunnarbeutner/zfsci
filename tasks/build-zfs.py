import os
from joblib import Task, TaskResult
from tasklib import Utility

class BuildZFSTask(Task):
	description = "Build ZFS"
	stage = "test"

	dependencies = ['zfs-builddeps', 'spl']
	provides = ['zfs']

	def prepare(self):
		try:
			os.mkdir("/root/build")
		except OSError:
			pass

		os.chdir("/root/build")
		os.system("rm -Rf /root/build/zfs")

		gitinfo = self.job.attributes['zfs-git-repo']

		repodir = "%s/repositories/%s" % (Utility.get_persistent_dir(), gitinfo['zfs-repository'])
		if os.system("git clone -b %s %s zfs" % (gitinfo['zfs-branch'], repodir)) != 0:
			return TaskResult.FAILED

		os.chdir("zfs")

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

		if os.system("modprobe zfs") != 0:
			return TaskResult.FAILED

		return TaskResult.PASSED

	def should_run(self):
		return (self.job.attributes['fs-type'] == 'zfs')

BuildZFSTask.register()
