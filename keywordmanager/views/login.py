import json
import os

import requests
from flask import g, render_template, request
from flask_login import login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
from werkzeug.utils import redirect

from keywordmanager import app
from keywordmanager.models.login.google_user import GoogleUser
from keywordmanager.models.login.login import LoginForm
from keywordmanager.models.login.user import User
from keywordmanager.utils.insert import conn


# Google auth init
GOOGLE_CLIENT_ID = "99303510174-uc50af88if08brvtqkb00edm93ifo8l5.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
client = WebApplicationClient(GOOGLE_CLIENT_ID)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@app.route("/", methods=['POST', 'GET'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect('/home')

    form = LoginForm()
    if form.validate_on_submit():
        user = conn('default').query(User).filter(User.email == form.email.data).first()
        login_user(user)
        return redirect('/home')
    return render_template('/login/login.html', form=form)


@app.route('/logingoogle')
def logingoogle():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route('/logingoogle/callback')
def logincallback():
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = GoogleUser(
        id=unique_id, name=users_name, email=users_email
    )

    if GoogleUser.get(unique_id) is None:
        GoogleUser.create(unique_id, users_name, users_email)

    login_user(user, remember=True)
    return redirect('/home')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')
