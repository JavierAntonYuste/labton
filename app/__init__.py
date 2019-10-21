from flask import Flask, url_for, redirect,  \
render_template, request, abort, session, flash

import csv, codecs

# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from flask_migrate import Migrate

from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password

from instance import config
from functools import wraps

from flask_sslify import SSLify
import datetime

from app import decorators, db_init

## IMAPLogin depende de la base de datos, por eso se importa despues de crearla
from app import IMAPLogin
login_manager = LoginManager()

def create_app(config_name):
    """ Main method of the server """

    global app
    # Creation of the app
    app = Flask(__name__, instance_relative_config=True)
    # Forced encription for deploying SSL connection
    sslify = SSLify(app, subdomains=True)

    # Chargin config
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from app import models

    # Setup Flask-Security
    global user_datastore
    user_datastore = SQLAlchemyUserDatastore(db_init.db, models.User, models.Role)
    # security = Security(app, user_datastore)
    # security = Security(app, user_datastore, login_form=IMAPLoginForm.IMAPLoginForm) ##Para cuando se haga IMAPLoginForm

    # Initialisation of the app and the system
    db_init.db.init_app(app)
    init_system()

    # Function of Flask-Login. User loader
    @login_manager.user_loader
    def load_user(email):
        return models.User.get(email)

    # Initialisation of Flask-Login
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

            #  IMAP Login attempt
            response=IMAPLogin.IMAPLogin(request.form['email'], request.form['password'])

            # Charging the username (first part of the email) in the session
            session["user"]=(request.form['email'].split('@'))[0]

            # If failed attempt, error
            if (response==False):
                error = 'Invalid Credentials. Please try again.'
            else:
                # Charging the email in an User object
                user = models.User()
                user.email = request.form['email']
                login_user(user)

                # Changing param of logged_in in session
                session['logged_in'] = True
                return redirect('/home')

        return render_template('login.html', error=error)

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        error = None
        # Clearing everything charged in session (id, username, logged_in, etc)
        session.clear()
        return render_template('index.html', error=error)

    @app.route('/home')
    @decorators.login_required
    def home():
        # Obtaining current year for showing the active subjects
        # An academic year is being considered (from 1/sep until 31/aug)
        now = datetime.datetime.now()
        if  now.month<9:
            current_year=now.year-1
        else:
            current_year=now.year

        # Querying database for taking the subjects that each user has access
        subjects = []
        user_id=db_init.db_session.query(models.User.id).filter_by(first_name=session["user"]).all()
        for item in user_id:
            subjects_id=db_init.db_session.query(models.users_subjects.c.subject_id).filter(models.users_subjects.c.user_id==item.id).all()
            for id in subjects_id:
                subjects.extend(db_init.db_session.query(models.Subject).filter_by(id=id,year=current_year).all())

        return render_template('home.html', user=session["user"], subjects= subjects)

    @app.route('/subject/<id>', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.roles_required('user')
    def subject(id):
        error = None
        subject=db_init.db_session.query(models.Subject).filter_by(id=id).all()
        return render_template('subject.html', error=error, user=session["user"], subject= subject)

    @app.route('/uploadUsers', methods=['POST'])
    def uploadUsers():
        ## TODO
        id = request.form['subject_id']
        if request.files['file']:
            flask_file = request.files['file']
            data = []
            stream = codecs.iterdecode(flask_file.stream, 'utf-8')
            for row in csv.reader(stream, dialect=csv.excel):
                if row:
                    data.append(row)

            print (data)
            print("")

            return redirect('/subject/'+ id)
        else:
            flash ("Error: It is not a valid input")
            return redirect('/subject/'+ id)

    @app.route('/uploadUser', methods=['POST'])
    def uploadUser():
        id = request.form['subject_id']
        if request.form['email']:
            name = (request.form['email'].split('@'))[0]
            user_id = db_init.db_session.query(models.User.id).filter_by(first_name=name).first()
            role = db_init.db_session.query(models.Role).filter_by(name='user').first()

            if (user_id == None):
                user= models.User(first_name=name, email= request.form['email'])
                user = user_datastore.create_user(
                    first_name=name,
                    email= request.form['email'],
                    roles=[models.Role(name='user')]
                )

                user_subject= ins = models.users_subjects.insert().values(
                subject_id= id,
                user_id = user_id,
                role_id=role.id
                )
                user_id = db_init.db_session.query(models.User.id).filter_by(first_name=name).first()
                db_init.db.session.commit()


            user_id = db_init.db_session.query(models.User.id).filter_by(first_name=name).first()
            user_subject= ins = models.users_subjects.insert().values(
            subject_id= id,
            user_id = user_id,
            role_id=role.id
            )
            conn = db_init.engine.connect()
            conn.execute(ins)

            return redirect('/subject/'+ id)
        else:
            flash ("Empty input")
            return redirect('/subject/'+ id)


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

        # Checking if table role exists, if not, return
        if not db_init.engine.dialect.has_table(db_init.engine, 'role'):
          return
        else:
            # Adding different core roles
            user_role = models.Role(name='user')
            professor_role = models.Role(name='professor')
            admin_role = models.Role(name='admin')

            if (models.Role.query.filter_by(name='user').first()==None):
                db_init.db.session.add(user_role)
            if (models.Role.query.filter_by(name='professor').first()==None):
                db_init.db.session.add(professor_role)
            if (models.Role.query.filter_by(name='admin').first()==None):
                db_init.db.session.add(admin_role)

            # Adding first user admin
            # IMPORTANT: delete after transferring admin role for security reasons
            if (models.User.query.filter_by(email='admin').first()==None):
                global user_datastore
                test_user = user_datastore.create_user(
                    first_name='Admin',
                    email='admin',
                    password='admin',
                    roles=[user_role, admin_role]
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
