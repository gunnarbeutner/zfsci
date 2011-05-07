from tasklib import Task, Utility

class DistributionAttribute(Attribute):
	name = "distribution"
	description = "Linux distribution"

	def get_values(self):
		config = Utility.get_zfsci_config()
		distsbasepath = config['persistent_path'] + '/dists'

		if not os.path.isdir(distsbasepath):
			try:
				os.makedirs(distsbasepath)
			except OSError:
				pass

		distsscriptdir = Utility.get_source_dir() + '/dists'

		distributions = [
			'debian',
			#'opensuse', # broken
			#'centos', # mostly works
			#'scientific' # horribly broken
		]

		for distribution in distributions:
			if not os.path.isfile("%s/%s.tar.gz" % (distsbasepath, distribution)):
				os.system("%s/%s.sh %s/%s.tar.gz" % (distsscriptdir, distribution, distsbasepath, distribution))

		return distributions

DistributionAttribute.register()
