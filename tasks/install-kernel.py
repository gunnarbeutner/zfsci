import os
import glob
from tasklib import Task

class InstallKernelTask(Task):
	description = "Linux kernel installation"
	stage = "build"

	def run(self):
		os.system("aptitude install -y wireless-crda")

		if os.system("dpkg -l | grep wireless-crda") != 0:
			if os.system("aptitude install -y equivs") != 0:
				return Task.FAILED

			fp = open("/tmp/wireless-crda", "w")
			fp.write("""
Section: misc
Priority: optional
Standards-Version: 3.6.2
Package: wireless-crda
""")
			fp.close()

			if os.system("equivs-build /tmp/wireless-crda") != 0:
				return Task.FAILED

			if os.system("dpkg -i wireless-crda_1.0_all.deb") != 0:
				return Task.FAILED

		if os.system("aptitude install -y initramfs-tools module-init-tools") != 0:
			return Task.FAILED

		kerneldir = "%s/kernels/%s/" % (Dispatcher.get_persistent_dir(), Dispatcher.get_input('kernel-version'))

		os.system("dpkg -i %s/*.deb" % (kerneldir))

		if not os.path.islink("/vmlinuz"):
			for kernel in glob.glob("/boot/vmlinuz*"):
				os.symlink(kernel, "/vmlinuz")
				break

		if not os.path.islink("/initrd.img"):
			for initrd in glob.glob("/boot/initrd*"):
				os.symlink(initrd, "/initrd.img")
				break

		return Task.PASSED

InstallKernelTask.register()
