import glob
from tasklib import Task, JobConfig

class DepmodTask(Task):
	description = "depmod"
	stage = "build"

	def run(self):
		for kernel in glob.glob("/boot/vmlinuz*"):
			file = os.path.basename(kernel)
			tokens = file.split('-', 1)

			if os.system("depmod %s" % tokens[1]) != 0:
				return Task.FAILED

			pass

		return Task.PASSED

DepmodTask.register()
