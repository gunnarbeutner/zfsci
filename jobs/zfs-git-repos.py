import os
from tasklib import Task, Utility

class ZFSGitRepoAttribute(Attribute):
	name = "zfs-git-repo"
	description = "ZFS git repositories"

	def get_values(self):
		repositories = [
			None,
			{
				'name': 'behlendorf',
				'spl': 'git://github.com/behlendorf/spl.git',
				'zfs': 'git://github.com/behlendorf/zfs.git'
			},
			{
				'name': 'gunnarbeutner',
				'spl': 'git://github.com/gunnarbeutner/pkg-spl.git',
				'zfs': 'git://github.com/gunnarbeutner/pkg-zfs.git'
			}
		]

		config = Utility.get_zfsci_config()
		repobasepath = config['persistent_path'] + '/repositories'

		if not os.path.isdir(repobasepath):
			try:
				os.makedirs(repobasepath)
			except OSError:
				pass

		os.chdir(repobasepath)

		values = [None]
		for repository in repositories:
			if repository == None:
				continue

			for subrepo in ['spl', 'zfs']:
				repodir = '%s-%s' % (repository['name'], subrepo)
				repopath = repobasepath + '/' + repodir

				if not os.path.isdir(repopath):
					os.system('git clone --mirror %s %s' % (repository[subrepo], repopath))

				os.system('GIT_DIR=%s git fetch' % (repopath))

			# TODO: list branches
			value = {
				'spl': '%s-spl' % (repository['name']),
				'zfs': '%s-zfs' % (repository['name']),
				'branch': 'master'
			}

			values.append(value)

		return values

	def validate_job(self, jobdesc):
		return (jobdesc['input']['fs-type'] == 'zfs' and \
			jobdesc['input']['zfs-git-repo'] != None) or \
			(jobdesc['input']['fs-type'] != 'zfs' and \
			jobdesc['input']['zfs-git-repo'] == None)

ZFSGitRepoAttribute.register()
