from flask import g, flash, render_template
from sqlalchemy import insert
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect

from keywordmanager import app
from keywordmanager.models.login.signup import SignupForm
from keywordmanager.models.login.user import User
from keywordmanager.utils.insert import conn


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