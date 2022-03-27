# coding: utf-8
from sqlalchemy import CHAR, Column, DECIMAL, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Job(Base):
    __tablename__ = 'jobs'

    job_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    title = Column(CHAR(45))
    description = Column(String(300), nullable=False)
    pay = Column(DECIMAL(3, 2), nullable=False)
    address = Column(String(64), nullable=False)
    state = Column(String(28), nullable=False)
    zipcode = Column(String(5), nullable=False)

class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    email = Column(String(45), nullable=False)
    password = Column(String(15), nullable=False)
    first = Column(CHAR(20), nullable=False)
    last = Column(CHAR(20), nullable=False)
    address = Column(String(64), nullable=False)
    state = Column(CHAR(28), nullable=False)
    zipcode = Column(String(5), nullable=False)
    is_admin = Column(String(45), nullable=False, server_default=text("'0'"))
