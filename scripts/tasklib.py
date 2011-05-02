import os
import json
import traceback
from time import time
import hashlib
import itertools

class Task(object):
	description = ""
	stage = "test"

	dependencies = []
	provides = []

	PENDING = 'PENDING'
	RUNNING = 'RUNNING'
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

		self.set_output('status', Task.RUNNING)

		try:
			status = self.prepare()

			if status == None or status == Task.PASSED:
				self.set_output('run_start', time())
				status = self.run()
				self.set_output('run_end', time())

			if status == None:
				status = Task.FAILED
		except Exception as exc:
			status = Task.FAILED

			self.set_output('exception', str(exc))
			self.set_output('stacktrace', traceback.format_exc())

			print exc

		try:
			self.finish()
		except Exception as exc:
			self.set_output('exception', str(exc))
			self.set_output('stacktrace', traceback.format_exc())

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

class Attribute(object):
	name = None
	description = ""

	_attributes = []

	def get_values(self):
		assert False

	def validate_job(self, jobdesc):
		return True

	@classmethod
	def register(cls):
		attr = cls()
		Attribute._attributes.append(attr)

	@staticmethod
	def hash_jobinput(jobinput):
		hash = hashlib.md5()

		for key in sorted(jobinput.iterkeys()):
			hash.update(key)

			value = jobinput[key]

			if type(value) == dict:
				for vkey in value:
					hash.update(vkey)
					hash.update(str(value[vkey]))
			elif value != None:
				hash.update(str(jobinput[key]))

		hash.digest()

		return hash.hexdigest()

	@staticmethod
	def _products(variants):
		# http://stackoverflow.com/questions/3873654/combinations-from-dictionary-with-list-values-using-python
		varNames = sorted(variants)
		return [
			dict(zip(varNames, prod))
			for prod in itertools.product(*(variants[varName] for varName in varNames))
		]

	@staticmethod
	def get_jobdescs():
		inputs = {}

		cwd = os.getcwd()
		for attr in Attribute._attributes:
			inputs[attr.name] = attr.get_values()
		os.chdir(cwd)

		jobdescs = []

		for jobinput in Attribute._products(inputs):
			jobhash = Attribute.hash_jobinput(jobinput)

			jobdesc = {
				'job_id': jobhash,
				'input': jobinput
			}

			validation_success = True
			for attr in Attribute._attributes:
				if not attr.validate_job(jobdesc):
					validation_success = False
					break

			if validation_success:
				jobdescs.append(jobdesc)

		return jobdescs

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
		return "/opt/zfsci/result_files/"

	@staticmethod
	def get_persistent_dir():
		return "/var/lib/zfsci-data/"

	@staticmethod
	def rearm_watchdog(timeout):
		os.system("/opt/zfsci/zfsci-watchdog %d" % (timeout))
