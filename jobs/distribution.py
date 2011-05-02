from tasklib import Task

class DistributionAttribute(Attribute):
	name = "distribution"
	description = "Linux distribution"

	def get_values(self):
		distsbasepath = '/var/lib/zfsci-data/dists'

		if not os.path.isdir(distsbasepath):
			try:
				os.makedirs(distsbasepath)
			except OSError:
				pass

		distsscriptdir = os.path.dirname(os.path.realpath(__file__)) + '/dists'

		distributions = [
			'debian'
		]

		for distribution in distributions:
			if not os.path.isfile("%s/%s.tar.gz" % (distsbasepath, distribution)):
				os.system("%s/%s.sh %s/%s.tar.gz" % (distsscriptdir, distribution, distsbasepath, distribution))

		return distributions

DistributionAttribute.register()
