import enum

from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class SearchKeyword(Base):
    __tablename__ = 'search'
    __table_args__ = {'schema': 'keywords'}
    id = Column('id', BigInteger, primary_key=True)
    keyword_id = Column('keyword_id', BigInteger)
    target_id = Column('target_id', BigInteger)
    target_type = Column('target_type', String)
    ad_group_id = Column('ad_group_id', BigInteger)
    created_time = Column('created_time', DateTime)
