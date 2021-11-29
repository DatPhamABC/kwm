import enum

from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Keyword(Base):
    __tablename__ = 'keyword'
    __table_args__ = {'schema': 'keywords'}
    id = Column('id', BigInteger, primary_key=True)
    word = Column('word', String, index=True)
    type = Column('type', String)
    is_active = Column('is_active', Boolean)
    created_time = Column('created_time', DateTime)
