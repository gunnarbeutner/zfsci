import os
import json
import traceback
import hashlib
import itertools
import uuid
from datetime import datetime

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

		os.chdir(cwd)

		return jobdescs

class Utility(object):
	_config = None

	@staticmethod
	def get_result_dir():
		return "/var/lib/zfsci"

	@staticmethod
	def get_persistent_dir():
		return "/var/lib/zfsci-data/"

	@staticmethod
	def get_scripts_dir():
		return os.path.realpath(os.path.dirname(__file__))

	@staticmethod
	def get_source_dir():
		return os.path.realpath(Utility.get_scripts_dir() + '/..')

	@staticmethod
	def get_tasks_dir():
		return Utility.get_persistent_dir() + '/tasks'

	@staticmethod
	def get_zfsci_config():
		if Utility._config != None:
			return Utility._config

		config = {}

		configfile = Utility.get_source_dir() + '/zfsci.conf'
		if not os.path.isfile(configfile):
			configfile = Utility.get_persistent_dir() + '/zfsci.conf'

		execfile(configfile, config)

		return config

	@staticmethod
	def rearm_watchdog(timeout):
		os.system("/opt/zfsci/zfsci-watchdog %d" % (timeout))

