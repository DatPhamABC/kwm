from flask import Flask

from flask_login import LoginManager

# Flask keywordmanager init
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = '511312c97a7bfbdaaee96cde'
app.config["SQLALCHEMY_ECHO"] = True

# Flask-login init
login_manager = LoginManager()
login_manager.init_app(app)

import keywordmanager.views.before_request
import keywordmanager.views.login
import keywordmanager.views.import_keyword
import keywordmanager.views.signup
import keywordmanager.views.home
import keywordmanager.views.search
import keywordmanager.views.keyword_edit
import keywordmanager.views.user_loader

app.run(debug=True)
