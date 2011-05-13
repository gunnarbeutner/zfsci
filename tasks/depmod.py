import glob
from joblib import Task

class DepmodTask(Task):
	description = "depmod"
	stage = "install"

	def run(self):
		for kernel in glob.glob("/boot/vmlinuz*"):
			file = os.path.basename(kernel)
			tokens = file.split('-', 1)

			if os.system("depmod %s" % tokens[1]) != 0:
				return TaskResult.FAILED

			pass

		return TaskResult.PASSED

DepmodTask.register()
