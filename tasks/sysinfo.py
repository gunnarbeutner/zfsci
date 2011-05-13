import glob
from joblib import Task, TaskResult
from partlib import PartitionBuilder

class SysInfoTask(Task):
	description = "System Information"
	stage = "install"

	def run(self):
		print "CPU (/proc/cpuinfo):"
		os.system("cat /proc/cpuinfo")
		print ""

		print "RAM (/proc/meminfo):"
		os.system("cat /proc/meminfo")
		print ""

		print "Network Information (ifconfig -a):"
		os.system("ifconfig -a")
		print ""

		install_device = PartitionBuilder.get_install_device()
		print "HDD (hdparm -i %s):" % (install_device)
		os.system("hdparm -i %s" % (install_device))

		return TaskResult.PASSED

SysInfoTask.register()
