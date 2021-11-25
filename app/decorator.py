from functools import wraps
from flask import redirect, request, g


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None or not g.user.is_authenticated:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function
