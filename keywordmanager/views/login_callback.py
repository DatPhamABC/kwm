import json

from flask import request
from flask_login import login_user
from google.auth.transport import requests
from werkzeug.utils import redirect

from keywordmanager.models.login.google_user import GoogleUser
from keywordmanager.utils.config import GOOGLE_DISCOVERY_URL, client, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


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