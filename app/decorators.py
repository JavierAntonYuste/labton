from flask import Flask, redirect,  \
render_template, request, abort, session, flash

from flask import current_app, g
from flask_login import current_user

from functools import wraps
from app import models
from app.db_init import db_session


## Decorators
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            # print("logged_in param in session")
            return f(*args, **kwargs)
        else:
            flash("Error! You need to login first", 'danger')
            return redirect("login")

    return wrap


def privileges_required(*privilege_names):
    def wrapper(view_function):

        @wraps(view_function)    # Tells debuggers that is is a function wrapper
        def decorator(*args, **kwargs):
            # User must have the required privileges

            for privilege_name in privilege_names:
                privilege_ids=db_session.query(models.Privilege.id).filter(models.Privilege.name==privilege_name).all()
            user_id = db_session.query(models.User.id).filter(models.User.email==session["email"]).all()

            for privilege_id in privilege_ids:
                users=db_session.query(models.privileges_users).filter_by(privilege_id=privilege_id).filter_by(user_id=user_id).all()
            if (users==[]):
                flash("Error! You don't have access to this page", 'danger')
                return redirect("home") ## redirect better to 403 forbidden

            return view_function(*args, **kwargs)
        return decorator
    return wrapper
