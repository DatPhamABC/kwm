from flask_login import UserMixin
from models.model import db


class GoogleUser(db.Model, UserMixin):
    __tablename__ = 'usergoogle'
    id = db.Column('id', db.String(100), primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))

    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    @staticmethod
    def get(user_id):
        user = GoogleUser.query.filter_by(id=user_id).first()
        return user

    @staticmethod
    def create(id, name, email):
        user = GoogleUser(id, name, email)
        db.session.add(user)
        db.session.commit()

    def get_name(self):
        return self.name