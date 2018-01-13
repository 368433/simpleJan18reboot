from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Sequence
from sqlalchemy import create_engine, Table, Text, distinct
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import time, platform
from random import randint



#############################################################
# ENGINE initialization
Base = declarative_base()
engine = create_engine('sqlite:///test.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

#####################################
class Patient(Base):
	__tablename__="patient"

	id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
	ramq = Column(String)
	mrn = Column(String)
	dob = Column(DateTime)
	phone = Column(String)
	fname = Column(String)
	lname = Column(String)
	postalcode = Column(String)
	is_active = Column(Boolean)
	is_inpatient = Column(Boolean)
	next_visit = Column(DateTime)
	last_seen = Column(String)
	is_female = Column(Boolean)
	idCard_path = Column(String)#the hash of the photo stored at capture/hash.jpeg	
	
	def __repr__(self):
		return "{0} {1} - mrn:{2}".format(self.fname, self.lname, self.mrn)
	
	def deepview(self):
		return "{0} {1}\n  MRN: {2}    RAMQ: {3}\n  DOB:{4}".format(self.fname, self.lname, self.mrn, self.ramq, self.dob.strftime("%d/%b/%Y"))
	
class Act(Base):
	__tablename__='act'
	
	id = Column(Integer, Sequence('user_id_seq'), unique=True, primary_key=True)
	subject = Column(String)
	date = Column(DateTime)
	root_act = Column(String)
	patient_id = Column(Integer)
	facility = Column(String)
	location = Column(String)
	category = Column(String)
	type = Column(String)
	diagnosis = Column(String)
	bed = Column(String)
	addendum = Column(String) #useful for extra info like type of MIEE, etc...
	act_photo_path = Column(String)# a comma separated list of hashes of the act’s note’s photo stored at capture/hash.jpeg
	
	def __repr__(self):
		return "{0}, Dx:{1}, Bed:{2}".format(self.type, self.diagnosis, self.bed)
	
def create_empty_db():
	Base.metadata.create_all(engine)
