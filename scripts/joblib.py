import os
import glob
import json
import hashlib
from sqlalchemy import types, create_engine, Column, String, Integer, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from tasklib import Utility

class JsonString(types.TypeDecorator):
	impl = types.Text

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

class Job(ModelBase):
	__tablename__ = 'jobs'

	id = Column(Integer, primary_key=True)
	hash = Column(String(32), unique=True)
	attributes = Column(JsonString)

	results = relationship('Result', backref='job')

	def __init__(self, hash):
		self.hash = hash

	@staticmethod
	def find_all(session):
		return session.query(Job).all()

	@staticmethod
	def find_by_hash(session, hash):
		return session.query(Job).filter(Job.hash == hash).first()

class Result(ModelBase):
	__tablename__ = 'results'

	id = Column(Integer, primary_key=True)
	job_id = Column(Integer, ForeignKey('jobs.id'))
	hash = Column(String(32), unique=True)
	timestamp = Column(Integer)
	attributes = Column(JsonString)

	def __init__(self, job, hash, timestamp):
		self.job = job
		self.hash = hash
		self.timestamp = timestamp

	@staticmethod
	def find_by_hash(session, hash):
		return session.query(Result).filter(Result.hash == hash).first()

	def count_errors(self):
		errors = 0

		for (task, taskinfo) in self.attributes.iteritems():
			if not 'status' in taskinfo or taskinfo['status'] not in ['PASSED', 'SKIPPED']:
				errors += 1

		return errors

def get_job_session():
	config = Utility.get_zfsci_config()

	engine = create_engine(config['job_dsn'])#, echo=True)
	ModelBase.metadata.create_all(engine)

	Session = sessionmaker()
	Session.configure(bind=engine)

	return Session()

def process_results(session):
	for resultdir in glob.glob(Utility.get_persistent_dir() + '/results/*'):
		try:
			resultfile = resultdir + '/job.json'

			fp = open(resultfile, 'r')
			resultinfo = json.load(fp)
			fp.close()

			statinfo = os.lstat(resultfile)
			timestamp = statinfo.st_mtime
		except Exception, exc:
			print exc
			continue

		job = Job.find_by_hash(session, resultinfo['job_id'])

		if job == None:
			job = Job(resultinfo['job_id'])
			job.attributes = resultinfo['input']
			session.add(job)

		if not 'output' in resultinfo:
			continue

		if not 'result_id' in resultinfo:
			resultinfo['result_id'] = hashlib.md5(os.path.basename(resultdir)).hexdigest()

		result = Result.find_by_hash(session, resultinfo['result_id'])

		if result == None:
			result = Result(job, resultinfo['result_id'], timestamp)
			result.attributes = resultinfo['output']
			session.add(result)

	session.commit()
