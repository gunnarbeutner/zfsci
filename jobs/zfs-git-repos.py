import os
import subprocess
from tasklib import Attribute, Utility

class ZFSGitRepoAttribute(Attribute):
	name = "zfs-git-repo"
	description = "ZFS git repositories"

	def get_values(self):
		repositories = [
			{
				'name': 'behlendorf',
				'spl': 'git://github.com/behlendorf/spl.git',
				'zfs': 'git://github.com/behlendorf/zfs.git',
				'zfs-ignore-branches': ['gh-pages']
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
			for subrepo in ['spl', 'zfs']:
				repodir = '%s-%s' % (repository['name'], subrepo)
				repopath = repobasepath + '/' + repodir

				if not os.path.isdir(repopath):
					os.chdir(repobasepath)
					os.system('git clone --mirror %s %s' % (repository[subrepo], repopath))

				os.chdir(repopath)
				os.system('git fetch')

				args = ['git', 'for-each-ref', '--format=%(refname:short)', 'refs/heads/']
				output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
				branches = output.strip().split('\n')

				for branch in branches:
					if subrepo + '-ignore-branches' in repository and \
							branch in repository[subrepo + '-ignore-branches']:
						continue

					args = ['git', 'rev-list', '--max-count=5', '--timestamp', branch]
					output = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

					commits = output.strip().split('\n')

					for commitinfo in commits:
						(timestamp, commit) = commitinfo.split(' ', 1)

						value = {
							'spl-repository': '%s-spl' % (repository['name']),
							'zfs-repository': '%s-zfs' % (repository['name']),
							'spl-branch': 'master',
							'zfs-branch': 'master',
							'timestamp': timestamp
						}

						value[subrepo + '-branch'] = branch

						values.append(value)

		return values

	def validate_job(self, jobdesc):
		return (jobdesc['input']['fs-type'] == 'zfs' and \
			jobdesc['input']['zfs-git-repo'] != None) or \
			(jobdesc['input']['fs-type'] != 'zfs' and \
			jobdesc['input']['zfs-git-repo'] == None)

ZFSGitRepoAttribute.register()
