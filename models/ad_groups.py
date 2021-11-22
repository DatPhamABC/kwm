from sqlalchemy import Column, BigInteger, Text, Numeric, String, JSON, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AdGroup(Base):
    __tablename__ = 'ad_groups'
    __table_args__ = {'schema': 'ads'}
    id = Column('id', BigInteger, primary_key=True)
    campaignid = Column('campaignid', BigInteger)
    campaignname = Column('campaignname', String)
    name = Column('name', String)
    status = Column('status', JSON)
    settings = Column('settings', JSON)
    biddingstrategyconfiguration = Column('biddingstrategyconfiguration', JSON)
    basecampaignid = Column('basecampaignid', BigInteger)
    baseadgroupid = Column('baseadgroupid', BigInteger)
    adgrouptype = Column('adgrouptype', JSON)
    adgroupadrotationmode = Column('adgroupadrotationmode', JSON)
    customerid = Column('customerid', String)
    __hevo_id = Column('__hevo_id', String)
    __hevo_report_date = Column('__hevo_report_date', Time)
    __hevo__ingested_at = Column('__hevo__ingested_at', BigInteger)
