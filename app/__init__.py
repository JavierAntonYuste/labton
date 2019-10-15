from flask import Flask, url_for, redirect,  \
render_template, request, abort, session, flash

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from flask_migrate import Migrate

from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password

from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from instance import config
from functools import wraps

from flask_sslify import SSLify
import datetime

from app import decorators

db = SQLAlchemy()
engine= create_engine(config.SQLALCHEMY_DATABASE_URI)
DB_Session = sessionmaker(bind=engine)
db_session = DB_Session()

## IMAPLogin depende de la base de datos, por eso se importa despues de crearla
from app import IMAPLogin
login_manager = LoginManager()


def create_app(config_name):
    global app
    app = Flask(__name__, instance_relative_config=True)
    sslify = SSLify(app, subdomains=True)

    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from app import models

    # Setup Flask-Security
    global user_datastore
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    # security = Security(app, user_datastore)
    # security = Security(app, user_datastore, login_form=IMAPLoginForm.IMAPLoginForm) ##Para cuando se haga IMAPLoginForm

    db.init_app(app)
    init_system()

    @login_manager.user_loader
    def load_user(email):
        return models.User.get(email)

    login_manager.init_app(app)
    login_manager.login_message = 'You must be logged in to access this page'


    # Routes
    @app.route('/')
    def root_directory():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':

            response=IMAPLogin.IMAPLogin(request.form['email'], request.form['password'])
            session["user"]=(request.form['email'].split('@'))[0]
            if (response==False):
                error = 'Invalid Credentials. Please try again.'
            else:
                user = models.User()
                user.email = request.form['email']
                login_user(user)

                session['logged_in'] = True
                return redirect('/home')

        return render_template('login.html', error=error)

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        error = None
        session.clear()
        return render_template('index.html', error=error)


    @app.route('/home')
    @decorators.login_required
    def home():
        #TODO Introduce year check and pass names to html
        now = datetime.datetime.now()
        if  now.month<9:
            current_year=now.year-1
        else:
            current_year=now.year

        subjects = []
        user_id=db_session.query(models.User.id).filter_by(first_name=session["user"]).all()
        for item in user_id:
            subjects_id=db_session.query(models.users_subjects.c.subject_id).filter(models.users_subjects.c.user_id==item.id).all()
            for id in subjects_id:
                subjects.extend(db_session.query(models.Subject).filter_by(id=id,year=current_year).all())
        error = None
        return render_template('home.html', error=error, user=session["user"], subjects= subjects)

    @app.route('/users')
    @decorators.login_required
    @roles_required('superuser')
    def users():

        error = None
        return render_template('users.html', error=error,user=session["user"])

    @app.route('/test')
    @decorators.login_required
    def test():
        with app.app_context():
            roles=models.Role.query.filter_by(name="superuser").all()
            id=(o.id for o in roles)
            print (next(id))

        return render_template('index.html')




    # define a context processor for merging flask-admin's template context into the
    # flask-security views.
        # @security.context_processor
        # def security_context_processor():
        #     return dict(
        #         admin_base_template=admin.base_template,
        #         admin_view=admin.index_view,
        #         h=admin_helpers,
        #         get_url=url_for
        #     )

    migrate = Migrate(app,db)

    return app


def init_system():
    global app
    with app.app_context():

        if not engine.dialect.has_table(engine, 'role'):
          return
        else:
            user_role = models.Role(name='user')
            super_user_role = models.Role(name='superuser')

            if (models.Role.query.filter_by(name='user').first()==None):
                db.session.add(user_role)
            if (models.Role.query.filter_by(name='superuser').first()==None):
                db.session.add(super_user_role)


            if (models.User.query.filter_by(email='admin').first()==None):
                global user_datastore
                test_user = user_datastore.create_user(
                    first_name='Admin',
                    email='admin',
                    password='admin',
                    roles=[user_role, super_user_role]
                )

                # superuser_id=models.Role.query.filter_by(name="superuser").all()
                # id=(o.id for o in superuser_id)
                #
                # if (session.query(models.roles_users).filter(models.roles_users.c.role_id==next(id)).first()==None):
                #     global user_datastore
                #     test_user = user_datastore.create_user(
                #         first_name='Admin',
                #         email='admin',
                #         password=encrypt_password('admin'),
                #         roles=[user_role, super_user_role]
                #     )

                db.session.commit()


def roles_required(*role_name):
    def wrapper(view_function):

        @wraps(view_function)    # Tells debuggers that is is a function wrapper
        def decorator(*args, **kwargs):

            # User must have the required roles
            ## TODO fixing decorator


            role_id = db_session.query(models.Role.id).filter(models.Role.name==role_name)
            user_id = db_session.query(models.User.id).filter(models.User.first_name==session["user"])

            if ((db_session.query(models.roles_users).filter_by(role_id=role_id, user_id=user_id).all())==None):

            # if (db_session.query(models.roles_users).filter(and_(models.roles_users.c.role_id==role_id, models.roles_users.c.user_id==user_id))==None):

                flash("You don't have access to this page")
                return redirect("home") ## redirect better to 403 forbidden

            return view_function(*args, **kwargs)
        return decorator
    return wrapper
