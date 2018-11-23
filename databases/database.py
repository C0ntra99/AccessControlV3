import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from databases.tableDef import *


engine = create_engine('sqlite:///databases/systemDB.db', echo=False)

class Database:

    def add(self, user):
        Session = sessionmaker(bind=engine)
        s = Session()
        s.add(user)
        s.commit()

    def remove(self, user):
        Session = sessionmaker(bind=engine)
        s = Session()
        q = s.query(User)
        s.delete(q.first())
        s.commit()

    def search(self, user):
        Session = sessionmaker(bind=engine)
        s = Session()
        q = s.query(User)
        for attr, value in user.items():
            q = q.filter(getattr(User, attr).like("%%%s%%" % value))
        return_list = list(q.all())

        return return_list

    def query(self, card):
        Session = sessionmaker(bind=engine)
        s = Session()
        q = s.query(User).filter(User.id==card)
        return_list = list(q.all())
        
        return return_list

    def addLog(self, log):
        Session = sessionmaker(bind=engine)
        s = Session()
        s.add(log)
        s.commit()
