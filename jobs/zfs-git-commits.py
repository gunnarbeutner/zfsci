import subprocess
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

		if jobdesc['input']['zfs-git-repo'] == None:
			return False

		config = Utility.get_zfsci_config()
		repobasedir = config['persistent_path'] + '/repositories'

		gitrepo = jobdesc['input']['zfs-git-repo']
		gitcommit = jobdesc['input']['zfs-git-commit']
		gitcommit_prev = gitcommit - ZFSGitCommitsAttribute.granularity

		found_different_commits = False
		for subrepo in ['spl', 'zfs']:
			repodir = gitrepo[subrepo]
			repopath = repobasedir + '/' + repodir

			os.chdir(repopath)
			args = ['git', 'rev-list', '--max-count=1', '--before=%d' % (gitcommit), gitrepo['branch']]
			commit = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

			args = ['git', 'rev-list', '--max-count=1', '--before=%d' % (gitcommit_prev), gitrepo['branch']]
			commit_prev = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

			if commit != commit_prev:
				found_different_commits = True

		return found_different_commits

ZFSGitCommitsAttribute.register()
