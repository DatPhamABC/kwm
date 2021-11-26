from sqlalchemy import Column, BigInteger, String, Float, Text, Numeric, SmallInteger, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Hotel(Base):
    __tablename__ = 'hotels'
    __table_args__ = {'schema': 'hotels'}
    id = Column('id', BigInteger, primary_key=True)
    hotel_name = Column('hotel_name', String)
    description = Column('description', Text)
    score = Column('score', Float)
    star_number = Column('star_number', BigInteger)
    category = Column('category', String)
    number_of_reviews = Column('number_of_reviews', BigInteger)
    priority = Column('priority', BigInteger)
    latitude = Column('latitude', Numeric(precision=10, scale=4))
    longitude = Column('longitude', Numeric(precision=10, scale=4))
    addr1 = Column('addr1', Text)
    district_id = Column('district_id', BigInteger)
    district_name = Column('district_name', String)
    province_id = Column('province_id', BigInteger)
    province_name = Column('province_name', String)
    sole_price = Column('sole_price', SmallInteger)
    best_seller = Column('best_seller', SmallInteger)
    hidden_price = Column('hidden_price', SmallInteger)
    updated_time = Column('updated_time', Time)
