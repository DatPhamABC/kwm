from sqlalchemy import Column, BigInteger, Text, Numeric
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class District(Base):
    __tablename__ = 'district'
    __table_args__ = {'schema': 'hotels'}
    id = Column('id', BigInteger, primary_key=True)
    provinceid = Column('provinceid', BigInteger)
    name = Column('name', Text)
    code = Column('code', Text)
    latitude = Column('latitude', Numeric)
    longitude = Column('longitude', Numeric)
    name_no_accent = Column('name_no_accent', Text)
    northeast_lat = Column('northeast_lat', Numeric)
    northeast_lng = Column('northeast_lng', Numeric)
    southwest_lat = Column('southwest_lat', Numeric)
    southwest_lng = Column('southwest_lng', Numeric)
    distance_from_northeast = Column('distance_from_northeast', Numeric)
    distance_from_southwest = Column('distance_from_southwest', Numeric)
