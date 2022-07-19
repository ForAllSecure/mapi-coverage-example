from datetime import date

from fastapi import Depends, FastAPI, HTTPException

import os

from pydantic import BaseModel

from typing import List

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy import Column, Integer, String
from sqlalchemy.types import Date

'''
Models / Schema
'''

Base = declarative_base()

class Record(Base):
    __tablename__ = "Records"

    id = Column(String, primary_key=True, index=True)
    date = Column(Date)
    country = Column(String(255), index=True)
    cases = Column(Integer)
    deaths = Column(Integer)
    recoveries = Column(Integer)

class RecordSchema(BaseModel):
    id: String
    date: date
    country: str
    cases: int
    deaths: int
    recoveries: int

    class Config:
        orm_mode = True

'''
Database setup
'''

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
 )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()

'''
FastAPI initialization
'''

app = FastAPI()

'''
REST API Endpoints
'''

@app.get("/records/", response_model=List[RecordSchema])
def show_records(db: Session = Depends(get_db)):
    records = db.query(Record).all()
    return records
