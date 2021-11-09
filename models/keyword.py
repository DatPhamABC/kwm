import enum

from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class typeEnum(enum.Enum):
    broad = "broad"
    phrase = "phrase"
    exact = "exact"


class Keyword(Base):
    __tablename__ = 'keyword'
    id = Column('id', BigInteger, primary_key=True)
    word = Column('word', String)
    type = Column('type', Enum(typeEnum))
    is_active = Column('is_active', Boolean)
    created_time = Column('created_time', DateTime)
