from sqlalchemy import Column, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class NegativeKeyword(Base):
    __tablename__ = 'negative'
    id = Column('id', BigInteger, primary_key=True)
    campaign_id = Column('campaign_id', BigInteger)
    ad_group_id = Column('ad_group_id', BigInteger)
    keyword_id = Column('keyword_id', BigInteger)
