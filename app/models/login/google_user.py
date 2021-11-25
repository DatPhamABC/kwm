from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import declarative_base
from flask_login import UserMixin

from app.utils.db_insert import conn

Base = declarative_base()


class GoogleUser(Base, UserMixin):
    __tablename__ = 'googleuser'
    __table_args__ = {'schema': 'keywords'}
    id = Column('id', String(50), primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    @staticmethod
    def get(user_id):
        user = conn('default').query(GoogleUser).filter(GoogleUser.id == user_id).first()
        return user

    @staticmethod
    def create(id, name, email):
        insert_db = insert(GoogleUser).values({'id': id, 'name': name, 'email': email})
        conn('default').execute(insert_db)

    def get_name(self):
        return self.name
