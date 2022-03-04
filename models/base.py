from sqlalchemy import Column, Integer, String, ForeignKey, Time, func, Boolean, Date,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from db.session import engine

Base = declarative_base()
class User(Base):
  __tablename__ = 'users'
  id = Column(Integer, primary_key=True, autoincrement=True, index=True)
  employee_number = Column(String(20),unique=True)
  name = Column(String(20))
  email = Column(String(30),unique=True)
  state = Column(Boolean)

class Part(Base):
  __tablename__='part'
  id = Column(Integer, primary_key=True, autoincrement=True, index=True)
  l_class  = Column(Integer,ForeignKey("large_class.id"))
  m_class  = Column(Integer,ForeignKey("midium_class.id"))
  s_class = Column(String(20),unique=True)
  max_count = Column(Integer)
  start_day = Column(Date)
  end_day = Column(Date)


class Raw(Base):
  __tablename__ = 'raw'
  id = Column(Integer, primary_key=True, autoincrement=True, index=True)
  part_id = Column(Integer,ForeignKey("part.id"))
  part  = relationship("Part")
  raw_name = Column(String(20))
  change_name = Column(String(20))
  chnage_day = Column(Date)

class Logs(Base):
  __tablename__ = "log"
  id = Column(Integer, primary_key = True, autoincrement=True,index=True)
  part_id = Column(Integer,ForeignKey("part.id"))
  part = relationship("Part")
  user_id = Column(Integer,ForeignKey("users.id"))
  user =  relationship("User")
  work_day = Column(Date)
  file_name = Column(String(20))
  info = Column(String(20))

class Test_log(Base):
  __tablename__ = "test_log"
  id = Column(Integer, primary_key = True, autoincrement=True,index=True)
  part_id = Column(Integer,ForeignKey("part.id"))
  part = relationship("Part")
  user_id = Column(Integer,ForeignKey("users.id"))
  user =  relationship("User")
  work_day = Column(Date)
  file_name = Column(String(20))
  info = Column(String(20))

class Error_list(Base):
  __tablename__ = 'error_list'
  id = Column(Integer, primary_key=True, autoincrement=True, index=True)
  error = Column(String(100))

class Error(Base):
  __tablename__= 'error'
  id = Column(Integer, primary_key=True, autoincrement=True, index=True)
  raw_id = Column(Integer,ForeignKey("raw.id"))
  raw = relationship("Raw")
  error_id =Column(Integer,ForeignKey("error_list.id"))
  error = relationship("Error_list")
  user_id = Column(Integer,ForeignKey("users.id"))
  user =  relationship("User")
  error_day = Column(Date)

if __name__ == "__main__":
  Base.metadata.create_all(bind=engine)