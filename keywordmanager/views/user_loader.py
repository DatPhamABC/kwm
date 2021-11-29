from keywordmanager import login_manager
from keywordmanager.models.login.google_user import GoogleUser
from keywordmanager.models.login.user import User
from keywordmanager.utils.insert import conn


@login_manager.user_loader
def load_user(user_id):
    if conn('default').query(User).filter(User.id == user_id).first() is not None:
        return conn('default').query(User).filter(User.id == user_id).first()
    if conn('default').query(GoogleUser).filter(GoogleUser.id == user_id).first() is not None:
        return conn('default').query(GoogleUser).filter(GoogleUser.id == user_id).first()