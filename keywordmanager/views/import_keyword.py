import pandas as pd
from flask import render_template, request, flash
from werkzeug.utils import redirect

from keywordmanager import app
from keywordmanager.utils import config
from keywordmanager.utils.XLSXparser import parse_xlsx
from keywordmanager.views.decorator import login_required


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
        if request.files['xlsxfile']:
            df1 = pd.read_excel(request.files['xlsxfile'], header=2)
            parse_xlsx(df1)
            return redirect('/import/notification')
        else:
            flash('Please choose your file.')
            return redirect('/import')
    return redirect('/')


@app.route("/import/notification")
@login_required
def notification():
    return render_template('/import/import-noti.html',
                           insert_count=config.new_insert_count,
                           update_count=config.update_count,
                           insert_data=config.insert_data,
                           update_data=config.update_data)
