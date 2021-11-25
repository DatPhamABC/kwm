from flask import app, request
from google.auth.transport import requests
from werkzeug.utils import redirect

from keywordmanager.utils.config import GOOGLE_DISCOVERY_URL, client


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