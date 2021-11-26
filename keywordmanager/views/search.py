import os

from flask import request, render_template

from keywordmanager import app
from keywordmanager.utils import config
from keywordmanager.utils.search import Filter, get_campaign_list, get_adgroup_list, get_province_list, \
    get_district_list, get_hotel_list
from keywordmanager.views.decorator import login_required


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