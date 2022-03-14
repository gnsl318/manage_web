

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from models import base


load_dotenv(verbose=True)
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

# window exe 로만들땐 DB_URL을 직접 적어서 넣어줘야함
engine = create_engine(SQLALCHEMY_DATABASE_URI,echo=False,pool_size=10,pool_recycle=200,pool_pre_ping=True)# timeout=600,pool_recycle=500)#,
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
        #session = SessionLocal()
