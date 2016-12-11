#!/usr/bin/env python
# -*- coding: utf8 -*-

from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_CONNECT_STRING = 'mysql+mysqldb://hackthon:hackthon1234.@123.207.234.128/hackthon?charset=utf8'

engine = create_engine(DB_CONNECT_STRING)
session_factory = sessionmaker(bind=engine)
BaseModel = declarative_base()


class Record(BaseModel):

    __tablename__ = "t_record"

    person_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), default=None)
    image_url = Column(Text)
    latitude = Column(String(11), default=None)
    longitude = Column(String(11), default=None)
    timestamp = Column(DateTime, default=None)
    remark = Column(Text, default=None)

BaseModel.metadata.create_all(engine)