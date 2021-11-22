from sqlalchemy import Column, BigInteger, Text, Numeric, String, JSON, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Campaign(Base):
    __tablename__ = 'campaigns'
    __table_args__ = {'schema': 'ads'}
    id = Column('id', BigInteger, primary_key=True)
    name = Column('name', String)
    status = Column('status', JSON)
    servingstatus = Column('servingstatus', JSON)
    startdate = Column('startdate', String)
    enddate = Column('enddate', String)
    budget = Column('budget', JSON)
    conversionoptimizereligibility = Column('conversionoptimizereligibility', JSON)
    adservingoptimizationstatus = Column('adservingoptimizationstatus', JSON)
    settings = Column('settings', JSON)
    advertisingchanneltype = Column('advertisingchanneltype', JSON)
    advertisingchannelsubtype = Column('advertisingchannelsubtype', JSON)
    networksetting = Column('networksetting', JSON)
    biddingstrategyconfiguration = Column('biddingstrategyconfiguration', JSON)
    campaigntrialtype = Column('campaigntrialtype', JSON)
    basecampaignid = Column('basecampaignid', BigInteger)
    universalappcampaigninfo = Column('universalappcampaigninfo', JSON)
    selectiveoptimization = Column('selectiveoptimization', JSON)
    customerid = Column('customerid', String)
    __hevo_id = Column('__hevo_id', String)
    __hevo_report_date = Column('__hevo_report_date', Time)
    __hevo__ingested_at = Column('__hevo__ingested_at', BigInteger)
