from flask import flash
from flask_wtf import FlaskForm
from keywordmanager.models.login.user import User
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import TextField, PasswordField, SubmitField
from wtforms.validators import Required, Email

from keywordmanager.utils.insert import conn


class LoginForm(FlaskForm):
    email = TextField('email', validators=[Required(), Email()])
    password = PasswordField('password', validators=[Required()])
    submit = SubmitField('login')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        user = conn('default').query(User).filter(User.email == self.email.data).first()
        if user is None:
            flash(message='You haven\'t create an account yet.', category='error')
            return False

        if not check_password_hash(user.password, self.password.data):
            print(user.password)
            print(generate_password_hash(self.password.data))
            flash(message='Wrong password.', category='error')
            return False

        self.user = user
        return True
