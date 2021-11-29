from flask import render_template

from keywordmanager import app
from keywordmanager.views.decorator import login_required


@app.route("/home")
@login_required
def home():
    return render_template('/home/home.html')