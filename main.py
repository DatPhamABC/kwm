from urllib.parse import unquote_plus

from werkzeug.utils import redirect
from flask import Flask, render_template, request
import pandas as pd

from db.db_search import Filter, get_campaign_list, get_adgroup_list, get_province_list, get_district_list, \
    get_hotel_list
from stored.XLSXparser import parse_xlsx
from stored import config

# Flask app init
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
        df1 = pd.read_excel(request.files['xlsxfile'], header=2)
        parse_xlsx(df1)
        return redirect('/import/notification')


@app.route("/import/notification")
def notifictation():
    return render_template('/import/import-noti.html',
                           insert_count=config.new_insert_count,
                           update_count=config.update_count)


@app.route("/search", methods=['GET'])
def search_home():
    filter = Filter(request.args.get('campaign-filter'),
                    request.args.get('adgroup-filter'),
                    request.args.get('province-filter'),
                    request.args.get('district-filter'),
                    request.args.get('hotel-filter'),
                    request.args.get('kwtype-filter'))
    print(filter.get_keyword_list())
    return render_template('/search/search.html',
                           campaign_list=get_campaign_list(),
                           adgroup_list=get_adgroup_list(),
                           province_list=get_province_list(),
                           district_list=get_district_list(),
                           hotel_list=get_hotel_list(),
                           keyword_list=filter.get_keyword_list())


@app.route("/edit/<id>+<name>+<form_type>+<match_type>+<level>+<level_name>")
def keyword_edit_negative(id, name, form_type, match_type, level, level_name):
    name = unquote_plus(name)
    form_type = unquote_plus(form_type)
    match_type = unquote_plus(match_type)
    level = unquote_plus(level)
    level_name = unquote_plus(level_name)
    return render_template('/edit/edit.html', name=name, form_type=form_type, match_type=match_type,
                           level=level, level_name=level_name)


@app.route("/edit/<id>+<name>+<form_type>+<match_type>+<level>+<level_name>+<target_name>+<target_type>",
           defaults={'target_name': None, 'target_type': None})
def keyword_edit_positive(id, name, form_type, match_type, level, level_name, target_name, target_type):
    name = unquote_plus(name)
    form_type = unquote_plus(form_type)
    match_type = unquote_plus(match_type)
    level = unquote_plus(level)
    level_name = unquote_plus(level_name)
    target_name = unquote_plus(target_name)
    target_type = unquote_plus(target_type)
    return render_template('/edit/edit.html', name=name, form_type=form_type, match_type=match_type,
                           level=level, level_name=level_name, target_name=target_name, target_type=target_type)


app.run(debug=True)
