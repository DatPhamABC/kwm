import traceback
from urllib.parse import unquote_plus

from flask import render_template, flash, request
from werkzeug.exceptions import BadRequest
from werkzeug.utils import redirect

from keywordmanager import app
from keywordmanager.utils.edit import get_keyword_info, delete_positive, delete_negative
from keywordmanager.utils.search import get_campaign_list, get_adgroup_list, get_hotel_list, get_district_list, \
    get_province_list
from keywordmanager.utils.update_change import update_change_negative, update_change_positive
from keywordmanager.views.decorator import login_required


edit_url = ""


@app.route("/edit/<id>")
@login_required
def keyword_edit(id):
    global edit_url
    keyword_info = get_keyword_info(unquote_plus(id))
    if keyword_info[2] == 'negative':
        edit_url = request.path
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
        edit_url = request.path
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
    global edit_url
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
            return redirect(edit_url)
        except BadRequest:
            flash('please input your change before save')
            traceback.print_exc()
            if not edit_url:
                return redirect(edit_url)
            else:
                return redirect('/')
    return redirect(edit_url)


@app.route('/edit/update/positive', methods=['GET', 'POST'])
@login_required
def edit_update_positive():
    global edit_url
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
            return redirect(edit_url)
        except BadRequest:
            flash('please input your change before save')
            traceback.print_exc()
            if not edit_url:
                return redirect(edit_url)
            else:
                return redirect('/')
    return redirect(edit_url)


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
