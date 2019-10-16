from flask import Flask, url_for, redirect,  \
render_template, request, abort, session, flash

# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from flask_migrate import Migrate

from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password

# from sqlalchemy import *
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker

from instance import config
from functools import wraps

from flask_sslify import SSLify
import datetime

from app import decorators, db_init

# db = SQLAlchemy()
# engine= create_engine(config.SQLALCHEMY_DATABASE_URI)
# DB_Session = sessionmaker(bind=engine)
# db_session = DB_Session()


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
    user_datastore = SQLAlchemyUserDatastore(db_init.db, models.User, models.Role)
    # security = Security(app, user_datastore)
    # security = Security(app, user_datastore, login_form=IMAPLoginForm.IMAPLoginForm) ##Para cuando se haga IMAPLoginForm

    db_init.db.init_app(app)
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
        now = datetime.datetime.now()
        if  now.month<9:
            current_year=now.year-1
        else:
            current_year=now.year

        subjects = []
        user_id=db_init.db_session.query(models.User.id).filter_by(first_name=session["user"]).all()
        for item in user_id:
            subjects_id=db_init.db_session.query(models.users_subjects.c.subject_id).filter(models.users_subjects.c.user_id==item.id).all()
            for id in subjects_id:
                subjects.extend(db_init.db_session.query(models.Subject).filter_by(id=id,year=current_year).all())
        error = None
        return render_template('home.html', error=error, user=session["user"], subjects= subjects)

    @app.route('/subject', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.roles_required('user')
    def subject():
        subject=db_init.db_session.query(models.Subject).filter_by(id=1).all()
        error = None
        print("hola")
        
        if request.method == 'POST':
            id=request.form['id']
            subject=db_init.db_session.query(models.Subject).filter(models.Subject.c.id==id).all()
            return render_template('subject.html', error=error, user=session["user"], subject= subject)
        else:
            return render_template('subject.html', error=error, user=session["user"], subject= subject)


    @app.route('/users')
    @decorators.login_required
    @decorators.roles_required('superuser')
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

    migrate = Migrate(app,db_init.db)

    return app


def init_system():
    global app
    with app.app_context():

        if not db_init.engine.dialect.has_table(db_init.engine, 'role'):
          return
        else:
            user_role = models.Role(name='user')
            super_user_role = models.Role(name='superuser')

            if (models.Role.query.filter_by(name='user').first()==None):
                db_init.db.session.add(user_role)
            if (models.Role.query.filter_by(name='superuser').first()==None):
                db_init.db.session.add(super_user_role)


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

                db_init.db.session.commit()
