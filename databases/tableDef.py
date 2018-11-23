from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

e = create_engine('sqlite:///databases/systemDB.db', echo=False)
b = declarative_base()

########################################################################
class User(b):
    """"""
    __tablename__ = "users"

    key = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    id = Column(String)

    #----------------------------------------------------------------------
    def __init__(self, name=None, email=None, id='test'):
        """"""
        self.name = name
        self.email = email
        self.id = id


class AccessLog(b):
    __tablename__ = "accesslogs"

    key = Column(Integer, primary_key=True)
    user = Column(String)
    event = Column(String)
    date = Column(DateTime)

    def __init__(self, user, event, date):

        self.user = user
        self.event = event
        self.date = date

class Admin(b):
	""""""
	__tablename__ = "admins"
	
	key = Column(Integer, primary_key=True)
	username = Column(String)
	password = Column(String)

class AdminLog(b):
	""""""
	__tablename__ = "adminlogs"
	
	key = Column(Integer, primary_key=True)
	event = Column(String)
	cause = Column(String)
	date = Column(DateTime)


# create tables
b.metadata.create_all(e)
