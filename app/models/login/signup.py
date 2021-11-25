from flask import flash
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, SubmitField
from wtforms.validators import Required, Email

from app.models.login.user import User
from app.utils.db_insert import conn


class SignupForm(FlaskForm):
    firstname = TextField('firstname', validators=[Required('Please enter your firstname')])
    lastname = TextField('lastname', validators=[Required('Please enter your lastname')])
    email = TextField('email',  validators=[Required('Please enter your email address.'),
                                            Email('Incorrect email format.')])
    password = PasswordField('password', validators=[Required('Please enter a password.')])
    confirm = PasswordField('confirm', validators=[Required('Please confirm your password')])
    submit = SubmitField('signup')

    def validate(self):
        user_email = conn('default').query(User.email).filter(User.email == self.email.data).first()
        if user_email:
            flash('You have already had an account.', category='error')
            return False
        if self.password.data != self.confirm.data:
            flash('Confirm password incorrect.', category='error')
            return False
        return True
