from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
 
#engine = create_engine('sqlite:///tutorial.db', echo=True)
#Base = declarative_base()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databases/systemDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
 
########################################################################
class Admin(db.Model):
	""""""
	__tablename__ = "admins"
	
	key = Column(Integer, primary_key=True)
	username = Column(db.String)
	password = Column(db.String)

class AdminLog(db.Model):
	""""""
	__tablename__ = "adminlogs"
	
	key = Column(Integer, primary_key=True)
	event = Column(db.String)
	cause = Column(db.String)
	date = Column(db.DateTime)

class User(db.Model):
    """"""
    __tablename__ = "users"

    key = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    id = Column(String)

class AccessLog(db.Model):
    __tablename__ = "accesslogs"

    key = Column(Integer, primary_key=True)
    user = Column(String)
    event = Column(String)
    date = Column(DateTime)
 
# create tables
#Base.metadata.create_all(engine)
