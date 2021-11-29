import os
import traceback

import pandas
from flask import request, render_template, flash, send_file
from werkzeug.utils import redirect

from keywordmanager import app
from keywordmanager.utils.search import Filter, get_campaign_list, get_adgroup_list, get_province_list, \
    get_district_list, get_hotel_list, delete_multiple
from keywordmanager.views.decorator import login_required


keyword_list = []
search_url = ""


@app.route("/search", methods=['GET'])
@login_required
def search_home():
    global keyword_list
    global search_url
    file_path = os.path.join(os.getcwd(), 'export.xlsx')
    if os.path.exists(file_path):
        os.remove(file_path)
    filter = Filter(request.args.get('campaign-filter'),
                    request.args.get('adgroup-filter'),
                    request.args.get('province-filter'),
                    request.args.get('district-filter'),
                    request.args.get('hotel-filter'),
                    request.args.get('kwtype-filter'))
    keyword_list = filter.get_keyword_list()
    search_url = request.url
    return render_template('/search/search.html',
                           campaign_list=get_campaign_list(),
                           adgroup_list=get_adgroup_list(),
                           province_list=get_province_list(),
                           district_list=get_district_list(),
                           hotel_list=get_hotel_list(),
                           keyword_list=keyword_list)


@app.route('/export')
@login_required
def export():
    global search_url
    global keyword_list
    if keyword_list:
        try:
            df = pandas.DataFrame(keyword_list)
            if df.shape[1] == 9:
                df.columns = ['ID', 'Search ID', 'Keyword', 'Match type', 'Level',
                              'Positive/Negative', 'Level name',
                              'Target name', 'Target type']
            else:
                df.columns = ['ID', 'Negative ID', 'Keyword', 'Match type', 'Level',
                              'Positive/Negative', 'Level name']
            file_path = os.path.join(os.getcwd(), 'export.xlsx')
            df.to_excel(file_path, index=False)
            return send_file(file_path, attachment_filename="export.xlsx")
        except Exception:
            traceback.print_exc()
    flash('Export failed.')
    if search_url:
        return redirect(search_url)
    else:
        return redirect('/')


@app.route("/search/delete", methods=['GET', 'POST'])
@login_required
def search_delete_multiple():
    if request.method == 'POST':
        data = request.json['data']
        delete_multiple(data)
    return redirect('/')