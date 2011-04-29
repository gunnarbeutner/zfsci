import os
import json

class Task(object):
	description = ""
	stage = "test"

	dependencies = []
	provides = []

	PENDING = 'PENDING'
	SKIPPED = 'SKIPPED'
	FAILED = 'FAILED'
	DEPENDENCY_ERROR = 'DEPENDENCY_ERROR'
	PASSED = 'PASSED'

	def __init__(self, output_properties):
		self.output_properties = output_properties
		self.dependencies_resolved = False

		if self.get_output('status', None) == None:
			self.set_output('status', Task.PENDING)

	def prepare(self):
		pass

	def run(self):
		pass

	def finish(self):
		pass

	def _run(self):
		assert self.get_output('status') == Task.PENDING

		if not self.dependencies_resolved:
			self.set_output('status', Task.DEPENDENCY_ERROR)
			return

		try:
			status = self.prepare()

			if status == None or status == Task.PASSED:
				status = self.run()

			if status == None:
				status = Task.FAILED
		except Exception as exc:
			status = Task.FAILED

			# TODO: store exc info
			print exc

		try:
			self.finish()
		except Exception as exc:
			# TODO: store exc info
			print exc

		self.set_output('status', status)

	def __str__(self):
		return self.description

	@classmethod
	def register(cls):
		Dispatcher.register_task(cls)

	def set_output(self, key, value):
		self.output_properties[key] = value

	def get_output(self, key, default=None):
		return self.output_properties.get(key, default)

class Dispatcher(object):
	tasks = []
	hive = None
	hivefile = None

	@staticmethod
	def register_task(taskcls):
		assert Dispatcher.hive != None

		if not 'output' in Dispatcher.hive:
			Dispatcher.hive['output'] = {}

		if not str(taskcls) in Dispatcher.hive['output']:
			Dispatcher.hive['output'][str(taskcls)] = {}

		taskobj = taskcls(Dispatcher.hive['output'][str(taskcls)])
		Dispatcher.tasks.append(taskobj)

	@staticmethod
	def run_stage(stage):
		for task in Dispatcher.tasks:
			if task.stage != stage:
				continue

			Dispatcher.run_task_once(task)

	@staticmethod
	def run_task_once(task):
		if task.get_output('status') != Task.PENDING:
			return

		task.dependencies_resolved = True

		for dependency in task.dependencies:
			depresolved = False

			for deptask in Dispatcher.tasks:
				if not dependency in deptask.provides:
					continue

				Dispatcher.run_task_once(deptask)

				if deptask.get_output('status') == Task.PASSED:
					depresolved = True

			if not depresolved:
				task.dependencies_resolved = False

		print "Running task '%s' (type %s)" % \
			(task, task.__class__)

		cwd = os.getcwd()
		Dispatcher.rearm_watchdog(7200)
		task._run()
		Dispatcher.rearm_watchdog(0)
		os.chdir(cwd)

		print "Task result: %s" % (task.get_output('status'))

		Dispatcher.save_hive()

	@staticmethod
	def set_input(key, value):
		Dispatcher.hive['input'][key] = value

	@staticmethod
	def get_input(key, default=None):
		return Dispatcher.hive['input'].get(key)

	@staticmethod
	def load_hive(hivefile):
		Dispatcher.hivefile = hivefile

		fp = open(Dispatcher.hivefile, 'r')
		Dispatcher.hive = json.load(fp)
		fp.close()

	@staticmethod
	def save_hive():
		assert Dispatcher.hive != None
		fp = open(Dispatcher.hivefile, 'w')
		json.dump(Dispatcher.hive, fp)

		# TODO: use a temp file and rename()
		fp.flush()
		os.fsync(fp.fileno())

		fp.close()

	@staticmethod
	def get_result_dir():
		return "/opt/zfsci/output_files/"

	@staticmethod
	def rearm_watchdog(timeout):
		os.system("/opt/zfsci/zfsci-watchdog %d" % (timeout))
