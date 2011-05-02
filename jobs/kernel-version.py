from tasklib import Task, Utility

class KernelVersionAttribute(Attribute):
	name = "kernel-version"
	description = "Linux kernel version"

	def get_values(self):
		config = Utility.get_zfsci_config()
		kernelbasepath = config['persistent_path'] + '/kernels'

		if not os.path.isdir(kernelbasepath):
			try:
				os.makedirs(kernelbasepath)
			except OSError:
				pass

		os.chdir(kernelbasepath)

		kernels = {
			'2.6.26': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.26/',
			'2.6.27': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.27/',
			'2.6.28': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.28/',
			'2.6.29': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.29/',
			'2.6.30': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.30/',
			'2.6.31': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.31/',
			'2.6.32': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.32/',
			'2.6.33': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.33/',
			'2.6.34': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.34-lucid/',
			'2.6.35': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.35-maverick/',
			'2.6.36': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.36-maverick/',
			'2.6.37': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.37-natty/',
			'2.6.38': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.38-natty/',
			'2.6.39': 'http://kernel.ubuntu.com/~kernel-ppa/mainline/v2.6.39-rc5-oneiric/'
		}

		for kernel in kernels.iterkeys():
			if os.path.islink(kernel):
				continue

			os.system("wget -r -np -c '%s'" % (kernels[kernel]))
			os.symlink(kernels[kernel][7:], kernel)

		return kernels.keys()

KernelVersionAttribute.register()
