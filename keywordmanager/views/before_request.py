from datetime import timedelta

from flask import g, session
from flask_login import current_user

from keywordmanager import app


@app.before_request
def before_request():
    g.user = current_user
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)

