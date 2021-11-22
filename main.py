import os
import traceback
from urllib.parse import unquote_plus

import pandas
from werkzeug.exceptions import BadRequest
from werkzeug.utils import redirect
from flask import Flask, render_template, request, flash, send_file
import pandas as pd

from utils.db_edit import get_keyword_info, delete_positive, delete_negative
from utils.db_search import Filter, get_campaign_list, get_adgroup_list, get_province_list, get_district_list, \
    get_hotel_list
from utils.XLSXparser import parse_xlsx
from utils import config

# Flask app init
from utils.db_update import update_change_negative, update_change_positive

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = '511312c97a7bfbdaaee96cde'


@app.route("/")
def redirect_home():
    return redirect("/home")


@app.route("/home")
def home():
    return render_template('home/home.html')


@app.route("/import")
def import_kw():
    return render_template('import/import.html')


@app.route("/import/xlsximport", methods=['POST', 'GET'])
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
def notifictation():
    return render_template('/import/import-noti.html',
                           insert_count=config.new_insert_count,
                           update_count=config.update_count,
                           insert_data=config.insert_data,
                           update_data=config.update_data)


@app.route("/search", methods=['GET'])
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
    config.sessions['search_url'] = request.path
    return render_template('/search/search.html',
                           campaign_list=get_campaign_list(),
                           adgroup_list=get_adgroup_list(),
                           province_list=get_province_list(),
                           district_list=get_district_list(),
                           hotel_list=get_hotel_list(),
                           keyword_list=config.sessions['keyword_list'])


@app.route("/edit/<id>")
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


app.run(debug=True)
