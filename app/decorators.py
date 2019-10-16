from flask import Flask, redirect,  \
render_template, request, abort, session, flash

from flask import current_app, g
from flask_login import current_user

from functools import wraps
from app import models, db_init


## Decorators
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            print("logged_in param in session")
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect("login")

    return wrap


def roles_required(*role_names):
    def wrapper(view_function):

        @wraps(view_function)    # Tells debuggers that is is a function wrapper
        def decorator(*args, **kwargs):
            # User must have the required roles

            for role_name in role_names:
                role_ids=db_init.db_session.query(models.Role.id).filter(models.Role.name==role_name).all()
            user_id = db_init.db_session.query(models.User.id).filter(models.User.first_name==session["user"]).all()

            for role_id in role_ids:
                users=db_init.db_session.query(models.roles_users).filter_by(role_id=role_id).filter_by(user_id=user_id).all()
            if (users==[]):
                flash("You don't have access to this page")
                return redirect("home") ## redirect better to 403 forbidden

            return view_function(*args, **kwargs)
        return decorator
    return wrapper
