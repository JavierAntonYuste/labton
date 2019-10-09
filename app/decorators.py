from flask import Flask, redirect,  \
render_template, request, abort, session, flash

from functools import wraps


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
