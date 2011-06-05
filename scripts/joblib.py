import os
import glob
import json
import hashlib
import traceback
from uuid import uuid4
from datetime import datetime, timedelta
from sqlalchemy import create_engine, and_, or_, Column, String, Integer, \
		ForeignKey, Text, DateTime, LargeBinary, Enum, Boolean
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, deferred
from tasklib import Utility

# TODO: change this to pickletype once we're sufficiently
# confident with the DB schema
class JsonString(TypeDecorator):
	impl = LargeBinary

	def __init__(*args, **kwargs):
		kwargs['length'] = 10 * 1024 * 1024;
		TypeDecorator.__init__(*args, **kwargs)

	def process_result_value(self, value, dialect):
		if value is None:
			return None
		else:
			return json.loads(value)

	def process_bind_param(self, value, dialect):
		if value is None:
			return None
		else:
			return json.dumps(value)

ModelBase = declarative_base()
JobSession = sessionmaker()

class Job(ModelBase):
	__tablename__ = 'jobs'

	hash = Column(String(32), primary_key=True)
	priority = Column(Integer, nullable=False)
	available = Column(Boolean, nullable=False, index=True)
	run_count = Column(Integer, nullable=False)
	last_run = Column(DateTime, index=True)
	attributes = deferred(Column(JsonString, nullable=False))

	results = relationship('JobResult', backref='job')

	def __init__(self, hash):
		self.hash = hash
		self.priority = 0
		self.available = True
		self.run_count = 0
		self.attributes = {}

	@staticmethod
	def find_all(session):
		return session.query(Job).all()

	@staticmethod
	def get_by_hash(session, hash):
		return session.query(Job).filter(Job.hash == hash).first()

	# TODO: test this, improve ordering
	# (e.g. by number of previous executions)
	@staticmethod
	def pick_job(session):
		connection = session.connection()

		connection.execute('LOCK TABLES jobs WRITE')

		bound_session = JobSession(bind=connection)

		query = bound_session.query(Job).filter(Job.available == True)
		query = query.order_by(Job.run_count.asc(), Job.last_run.asc(), Job.priority.asc())

		job = query.first()

		if job != None:
			job.available = False
			job.run_count += 1
			job.last_run = datetime.now()

		bound_session.commit()

		connection.execute('UNLOCK TABLES')

		# merge the job object into the right session
		if job != None:
			job = session.merge(job)

		return job

class JobResult(ModelBase):
	__tablename__ = 'jobresults'

	SUCCESS = 'SUCCESS'
	BUILD_ERROR = 'BUILD_ERROR'
	SYSTEM_ERROR = 'SYSTEM_ERROR'

	hash = Column(String(32), primary_key=True)
	job_hash = Column(String(32), ForeignKey('jobs.hash'), nullable=False)
	run_start = Column(DateTime, nullable=False)
	run_end = Column(DateTime)
	attributes = deferred(Column(JsonString, nullable=False))

	taskresults = relationship('TaskResult', backref='jobresult')

	def __init__(self, job, hash=None):
		self.job = job

		if hash == None:
			hash = uuid4().hex
			
		self.hash = hash
		self.run_start = datetime.now()
		self.attributes = {}

	@staticmethod
	def get_by_hash(session, hash):
		return session.query(JobResult).filter(JobResult.hash == hash).first()

	@staticmethod
	def get_configured_jobresult(session, in_chroot):
		idfile = Utility.get_result_dir()  + '/result-id'

		if not in_chroot:
			idfile = '/mnt/' + idfile

		if not os.path.isfile(idfile):
			return None

		fp = open(idfile, 'r')
		result_hash = fp.read().strip()
		fp.close()

		return JobResult.get_by_hash(session, result_hash)

	def set_configured_jobresult(self, in_chroot):
		idfile = Utility.get_result_dir()  + '/result-id'

		if not in_chroot:
			idfile = '/mnt/' + idfile

		fp = open(idfile, 'w')
		fp.write(self.hash)
		fp.close

	def count_errors(self):
		errors = 0

		for taskresult in self.taskresults:
			if not taskresult.status in [TaskResult.PASSED, TaskResult.SKIPPED]:
				errors += 1

		return errors

	def get_result_type(self):
		seen_test_stage = False

		for taskresult in self.taskresults:
			if taskresult.status in [TaskResult.PENDING, TaskResult.RUNNING]:
				return JobResult.SYSTEM_ERROR
			elif taskresult.status not in [TaskResult.PASSED, TaskResult.SKIPPED]:
				return JobResult.BUILD_ERROR

			if taskresult.stage == 'test':
				seen_test_stage = True

		if not seen_test_stage:
			return JobResult.SYSTEM_ERROR

		return JobResult.SUCCESS

	def get_task(self, name, create=False):
		session = JobSession.object_session(self)

		where = and_(TaskResult.jobresult == self, TaskResult.name == name)
		taskresult = session.query(TaskResult).filter(where).first()

		if taskresult != None or create == False:
			return taskresult

		taskresult = TaskResult(self, name)
		session.add(taskresult)

		return taskresult



class TaskResult(ModelBase):
	__tablename__ = 'taskresults'

	PENDING = 'PENDING'
	RUNNING = 'RUNNING'
	SKIPPED = 'SKIPPED'
	FAILED = 'FAILED'
	DEPENDENCY_ERROR = 'DEPENDENCY_ERROR'
	PASSED = 'PASSED'

	id = Column(Integer, primary_key=True)
	jobresult_hash = Column(String(32), ForeignKey('jobresults.hash'), nullable=False)
	name = Column(String(64), nullable=False)
	stage = Column(Enum('install', 'test', 'post'))
	run_start = Column(DateTime)
	run_end = Column(DateTime)
	status = Column(Enum(PENDING, RUNNING, SKIPPED, FAILED, DEPENDENCY_ERROR, PASSED), nullable=False)
	attributes = Column(JsonString, nullable=False)
	output = deferred(Column(LargeBinary(10 * 1024 * 1024)))

	def __init__(self, jobresult, name):
		self.jobresult = jobresult
		self.name = name
		self.status = TaskResult.PENDING
		self.attributes = {}

class Task(object):
	description = ""
	stage = "test"

	dependencies = []
	provides = []

	def __init__(self):
		self.dependencies_resolved = False
		self.result = None

	def prepare(self):
		pass

	def run(self):
		pass

	def finish(self):
		pass

	def should_run(self):
		return True

	def _run(self):
		assert self.result.status == TaskResult.PENDING

		if not self.should_run():
			self.result.status = TaskResult.SKIPPED
			return

		if not self.dependencies_resolved:
			self.result.status = TaskResult.DEPENDENCY_ERROR
			return

		clshash = hashlib.md5(str(self.__class__)).hexdigest()
		outputfile = Utility.get_result_dir() + '/output_' + clshash
		outputfp = open(outputfile, "w")

		stdoutfd = os.dup(1)
		stderrfd = os.dup(2)

		os.dup2(outputfp.fileno(), 1)
		os.dup2(outputfp.fileno(), 2)

		self.result.status = TaskResult.RUNNING
		JobSession.object_session(self.result).commit()

		try:
			status = self.prepare()

			if status == None or status == TaskResult.PASSED:
				self.result.run_start = datetime.now()
				status = self.run()
				self.result.run_end = datetime.now()
			if status == None:
				status = TaskResult.FAILED
		except Exception, exc:
			status = TaskResult.FAILED

			self.result.attributes['exception'] = str(exc)
			self.result.attributes['stacktrace'] = traceback.format_exc()

			print exc

		try:
			self.finish()
		except Exception, exc:
			self.result.attributes['exception'] = str(exc)
			self.result.attributes['stacktrace'] = traceback.format_exc()

			print exc

		self.result.status = status

		os.dup2(stdoutfd, 1)
		os.dup2(stderrfd, 2)

		os.close(stdoutfd)
		os.close(stderrfd)

		outputfp.close()

		outputfp = open(outputfile, "r")
		output = outputfp.read()
		self.result.output = output
		outputfp.close()

		os.unlink(outputfile)

	@classmethod
	def register(cls):
		JobDispatcher._register_task(cls)

class JobDispatcher(object):
	tasks = []

	def __init__(self, jobresult):
		assert jobresult != None

		self.jobresult = jobresult

	@staticmethod
	def _register_task(taskcls):
		taskobj = taskcls()
		JobDispatcher.tasks.append(taskobj)

	def run_stage(self, stage):
		self.jobresult.attributes['stage_%s_start' % (stage)] = datetime.now()

		for taskfile in glob.glob('%s/*.py' % (Utility.get_tasks_dir())):
			execfile(taskfile, globals())

		for task in JobDispatcher.tasks:
			if task.stage != stage:
				continue

			self._run_task_once(task)

		self.jobresult.attributes['stage_%s_end' % (stage)] = datetime.now()

	def _run_task_once(self, task):
		if task.result != None and task.result.status != TaskResult.PENDING:
			return

		task.job = self.jobresult.job
		task.result = self.jobresult.get_task(str(task.__class__), True)
		task.result.stage = task.stage
		task.dependencies_resolved = True

		for dependency in task.dependencies:
			depresolved = False

			for deptask in JobDispatcher.tasks:
				if not dependency in deptask.provides:
					continue

				self._run_task_once(deptask)

				if deptask.result.status == TaskResult.PASSED:
					depresolved = True

			if not depresolved:
				task.dependencies_resolved = False

		print "Running task '%s' (type %s)" % \
			(task.description, task.__class__)

		cwd = os.getcwd()
		Utility.rearm_watchdog(1800)
		task._run()
		Utility.rearm_watchdog(0)
		os.chdir(cwd)

		print "Task result: %s" % (task.result.status)

		JobSession.object_session(self.jobresult).commit()

def get_job_session(debug=False):
	config = Utility.get_zfsci_config()
	engine = create_engine(config['job_dsn'], echo=debug)
	ModelBase.metadata.create_all(engine)

	return JobSession(bind=engine)

def process_results(session):
	for resultdir in glob.glob(Utility.get_persistent_dir() + '/results/*'):
		try:
			resultfile = resultdir + '/job.json'

			fp = open(resultfile, 'r')
			resultinfo = json.load(fp)
			fp.close()

			statinfo = os.lstat(resultfile)
			timestamp = datetime.fromtimestamp(statinfo.st_mtime)
		except Exception, exc:
			print exc
			continue

		job = Job.get_by_hash(session, resultinfo['job_id'])

		if job == None:
			job = Job(resultinfo['job_id'])
			job.attributes = resultinfo['input']
			session.add(job)

		if not 'output' in resultinfo:
			continue

		if not 'result_id' in resultinfo:
			resultinfo['result_id'] = hashlib.md5(os.path.basename(resultdir)).hexdigest()

		result = JobResult.get_by_hash(session, resultinfo['result_id'])

		if result == None:
			jobresult = JobResult(job, resultinfo['result_id'])

			for (task, taskinfo) in resultinfo['output'].iteritems():
				taskresult = TaskResult(jobresult, task)
				taskresult.attributes =  taskinfo
				session.add(taskresult)

			session.add(jobresult)

	session.commit()
