from sqlalchemy import Column, BigInteger, Text, Numeric, String, JSON, Time
from sqlalchemy.orm import declarative_base
from flask_login import UserMixin
Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'userinfo'
    __table_args__ = {'schema': 'keywords'}
    id = Column('id', BigInteger, primary_key=True)
    firstname = Column('firstname', String(50))
    lastname = Column('lastname', String(50))
    email = Column('email', String(50))
    password = Column('password', String(255))

    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password

    def get_name(self):
        return self.lastname

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    @staticmethod
    def get(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user
