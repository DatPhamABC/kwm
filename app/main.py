import os
import traceback
from urllib.parse import unquote_plus

import pandas
from sqlalchemy.dialects.mysql import insert
from werkzeug.exceptions import BadRequest
from flask import Flask, render_template, request, flash, send_file, g
import pandas as pd

from app.utils.db_edit import get_keyword_info, delete_positive, delete_negative
from app.utils.db_insert import conn
from app.utils.db_search import Filter, get_campaign_list, get_adgroup_list, get_province_list, get_district_list, \
    get_hotel_list, delete_multiple
from app.utils.XLSXparser import parse_xlsx
from app.utils import config
from app.utils.db_update import update_change_negative, update_change_positive
import json

import requests
from flask_login import LoginManager, current_user, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect
from app.decorator import login_required
from app.models.login.login import LoginForm
from app.models.login.signup import SignupForm
from app.models.login.user import User
from app.models.login.google_user import GoogleUser


# Flask app init
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = '511312c97a7bfbdaaee96cde'

# Google auth init
GOOGLE_CLIENT_ID = "99303510174-uc50af88if08brvtqkb00edm93ifo8l5.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
client = WebApplicationClient(GOOGLE_CLIENT_ID)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Flask-login init
login_manager = LoginManager()
login_manager.init_app(app)


@app.before_request
def before_request():
    g.user = current_user


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


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if g.user is not None and g.user.is_authenticated:
        return redirect('/home')
    form = SignupForm()
    if form.validate_on_submit():
        insert_db = insert(User).values({'firstname': form.firstname.data,
                                         'lastname': form.lastname.data,
                                         'email': form.email.data,
                                         'password': generate_password_hash(form.password.data)})
        conn('default').execute(insert_db)
        flash('Signed up successfully.')
        return redirect('/')
    return render_template('/login/signup.html')


@app.route("/home")
@login_required
def home():
    return render_template('/home/home.html')


@app.route("/import")
@login_required
def import_kw():
    return render_template('/import/import.html')


@app.route("/import/xlsximport", methods=['POST', 'GET'])
@login_required
def import_xlsx():
    if request.method == "POST":
        config.update_count = 0
        config.new_insert_count = 0
        config.update_data = []
        config.insert_data = []
        df1 = pd.read_excel(request.files['xlsxfile'], header=2)
        parse_xlsx(df1)
        return redirect('/import/notification')


@app.route("/import/notification")
@login_required
def notification():
    return render_template('/import/import-noti.html',
                           insert_count=config.new_insert_count,
                           update_count=config.update_count,
                           insert_data=config.insert_data,
                           update_data=config.update_data)


@app.route("/search", methods=['GET'])
@login_required
def search_home():
    file_path = os.path.join(os.getcwd(), 'export.xlsx')
    if os.path.exists(file_path):
        os.remove(file_path)
    filter = Filter(request.args.get('campaign-filter'),
                    request.args.get('adgroup-filter'),
                    request.args.get('province-filter'),
                    request.args.get('district-filter'),
                    request.args.get('hotel-filter'),
                    request.args.get('kwtype-filter'))
    config.sessions['keyword_list'] = filter.get_keyword_list()
    config.sessions['search_url'] = request.url
    return render_template('/search/search.html',
                           campaign_list=get_campaign_list(),
                           adgroup_list=get_adgroup_list(),
                           province_list=get_province_list(),
                           district_list=get_district_list(),
                           hotel_list=get_hotel_list(),
                           keyword_list=config.sessions['keyword_list'])


@app.route("/search/delete", methods=['GET', 'POST'])
@login_required
def search_delete_multiple():
    if request.method == 'POST':
        data = request.json['data']
        delete_multiple(data)
    return redirect('/')


@app.route("/edit/<id>")
@login_required
def keyword_edit(id):
    keyword_info = get_keyword_info(unquote_plus(id))
    if keyword_info[2] == 'negative':
        config.sessions['edit_url'] = request.path
        return render_template('/edit/edit_negative.html',
                               id=keyword_info[0],
                               keyword=keyword_info[1],
                               form_type=keyword_info[2],
                               match_type=keyword_info[3],
                               level=keyword_info[4],
                               campaign_name=keyword_info[5],
                               ad_group_name=keyword_info[6],
                               negative_id=keyword_info[7],
                               campaign_list=get_campaign_list(),
                               adgroup_list=get_adgroup_list())
    if keyword_info[2] == 'positive':
        config.sessions['edit_url'] = request.path
        hotel = None
        district = None
        province = None
        if keyword_info[6] == 'hotels':
            hotel = keyword_info[7]
        elif keyword_info[6] == 'province':
            province = keyword_info[7]
        elif keyword_info[6] == 'district':
            district = keyword_info[7]
        return render_template('/edit/edit_positive.html',
                               id=keyword_info[0],
                               keyword=keyword_info[1],
                               form_type=keyword_info[2],
                               match_type=keyword_info[3],
                               level=keyword_info[4],
                               ad_group_name=keyword_info[5],
                               target_type=keyword_info[6],
                               hotel=hotel,
                               district=district,
                               province=province,
                               positive_id=keyword_info[8],
                               adgroup_list=get_adgroup_list(),
                               hotel_list=get_hotel_list(),
                               district_list=get_district_list(),
                               province_list=get_province_list())
    flash('Fail to load edit.')
    return redirect('/')


@app.route('/edit/update/negative', methods=['GET', 'POST'])
@login_required
def edit_update_negative():
    if request.method == "POST":
        try:
            flash('Update successfully.')
            keyword = request.form['keyword']
            match_type = request.form['match_type']
            old_adgroup = request.form['old_adgroup']
            adgroup = request.form['adgroup']
            old_campaign = request.form['old_campaign']
            campaign = request.form['campaign']
            update_change_negative(keyword, match_type, old_adgroup, adgroup, old_campaign, campaign)
            return redirect(config.sessions['edit_url'])
        except BadRequest:
            flash('please input your change before save')
            traceback.print_exc()
            if 'edit_url' in config.sessions:
                return redirect(config.sessions['edit_url'])
            else:
                return redirect('/')
    return redirect(config.sessions['edit_url'])


@app.route('/edit/update/positive', methods=['GET', 'POST'])
@login_required
def edit_update_positive():
    if request.method == "POST":
        try:
            keyword = request.form['keyword']
            match_type = request.form['match_type']
            adgroup = request.form['adgroup']
            target_type = request.form['target_type']
            hotel = request.form['hotel']
            district = request.form['district']
            province = request.form['province']
            update_change_positive(keyword, match_type, adgroup, target_type, hotel, district, province)
            flash('Update successfully.')
            return redirect(config.sessions['edit_url'])
        except BadRequest:
            flash('please input your change before save')
            traceback.print_exc()
            if 'edit_url' in config.sessions:
                return redirect(config.sessions['edit_url'])
            else:
                return redirect('/')
    return redirect(config.sessions['edit_url'])


@app.route('/edit/delete', methods=['POST', 'GET'])
@login_required
def edit_delete():
    if request.method == 'POST':
        if "delete-positive-id" in request.form:
            delete_positive(request.form['delete-keyword-id'], request.form['delete-positive-id'])
            flash("Delete successfully.")
            return redirect('/')
        if "delete-negative-id" in request.form:
            delete_negative(request.form['delete-keyword-id'], request.form['delete-negative-id'])
            flash("Delete successfully.")
        return redirect('/')


@app.route('/export')
@login_required
def export():
    if 'keyword_list' in config.sessions:
        try:
            df = pandas.DataFrame(config.sessions['keyword_list'])
            if df.shape[1] == 8:
                df.columns = ['ID', 'Keyword', 'Match type', 'Level',
                              'Positive/Negative', 'Level name',
                              'Target name', 'Target type']
            else:
                df.columns = ['ID', 'Keyword', 'Match type', 'Level',
                              'Positive/Negative', 'Level name']
            file_path = os.path.join(os.getcwd(), 'export.xlsx')
            df.to_excel(file_path, index=False)
            return send_file(file_path, attachment_filename="export.xlsx")
        except Exception:
            traceback.print_exc()
    flash('Export failed.')
    if 'search_url' in config.sessions:
        return redirect(config.sessions['search_url'])
    else:
        return redirect('/')


@login_manager.user_loader
def load_user(user_id):
    if conn('default').query(User).filter(User.id == user_id).first() is not None:
        return conn('default').query(User).filter(User.id == user_id).first()
    if conn('default').query(GoogleUser).filter(GoogleUser.id == user_id).first() is not None:
        return conn('default').query(GoogleUser).filter(GoogleUser.id == user_id).first()


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


app.run(debug=True)
