from tasklib import Task, Dispatcher

class TestTask(Task):
	description = "Some test task"
	stage = "zzt"

	def run(self):
		print "TestTask:run"

		print "fs_type prop: %s" % (Dispatcher.get_input('fs_type'))

		return Task.PASSED

TestTask.register()
