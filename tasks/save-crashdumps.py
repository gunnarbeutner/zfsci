import glob
import shutil
from tasklib import Task, Utility

class SaveCrashDumpsTask(Task):
	description = "Save kernel crash dumps"
	stage = "post"

	def run(self):
		for file in glob.glob("/var/crash/[0-9]*/*"):
			shutil.copy(file, Utility.get_result_dir())

		return Task.PASSED

SaveCrashDumpsTask.register()
