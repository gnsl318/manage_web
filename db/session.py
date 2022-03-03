from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(verbose=True)
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')

# window exe 로만들땐 DB_URL을 직접 적어서 넣어줘야함
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
