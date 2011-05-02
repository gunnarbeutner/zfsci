from tasklib import Task
from time import time

class ZFSGitCommitsAttribute(Attribute):
	name = "zfs-git-commit"
	description = "ZFS git commits"

	interval = 7 * 24 * 60 * 60
	granularity = 2 * 60 * 60

	def get_values(self):
		now = time()
		end = now - (now % ZFSGitCommitsAttribute.granularity)

		commits = [None]
		for i in range(ZFSGitCommitsAttribute.interval / ZFSGitCommitsAttribute.granularity):
			commits.append(int(end - i * ZFSGitCommitsAttribute.granularity))

		return commits

	def validate_job(self, jobdesc):
		if jobdesc['input']['fs-type'] != 'zfs':
			return jobdesc['input']['zfs-git-commit'] == None

		if jobdesc['input']['fs-type'] == 'zfs' and \
				jobdesc['input']['zfs-git-commit'] == None:
			return False

		# TODO: check whether this is a "unique" commit for the current repo
		return True

ZFSGitCommitsAttribute.register()
