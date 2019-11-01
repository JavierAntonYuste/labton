from flask import Flask, url_for, redirect,  \
render_template, request, abort, session, flash

import csv, codecs, os, datetime

# from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from flask_migrate import Migrate

from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password

from instance import config
from functools import wraps

from flask_sslify import SSLify
import datetime
from app import decorators
from app.db_init import init_db, db, db_session, engine
from app.db_interactions import *


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

    # Initialisation of the app and the system
    db.init_app(app)
    init_db()
    init_system()


    # Function of Flask-Login. User loader
    @login_manager.user_loader
    def load_user(email):
        return models.User.get(email)

    # Initialisation of Flask-Login
    login_manager.init_app(app)
    login_manager.login_message = 'You must be logged in to access this page'

    # Before request Function
    # @app.before_request
    # def before_request_func():
    #     init_db()
    #     init_system()

    #Close session after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # Routes
    @app.route('/')
    def root_directory():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':

            #  IMAP Login attempt
            response=IMAPLogin.IMAPLogin(db_session, engine, request.form['email'], request.form['password'])

            # Charging the username (first part of the email) in the session
            session["email"]=request.form['email']

            # If failed attempt, error
            if (response==False):
                flash('Invalid credentials', 'danger')
                return redirect('/login')

            else:
                # Changing param of logged_in in session
                session['logged_in'] = True
                return redirect('/home')

        return render_template('login.html')

    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        # Clearing everything charged in session (id, username, logged_in, etc)
        session.clear()
        return render_template('index.html')

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
        user_id=get_user_id(db_session,session["email"])
        privileges=get_privileges(db_session, session["email"] )
        print (privileges)
        print ("")

        subjects_id=db_session.query(models.users_subjects.c.subject_id).filter(models.users_subjects.c.user_id==user_id).all()
        for id in subjects_id:
            subjects.extend(db_session.query(models.Subject).filter_by(id=id,year=current_year).all())

        user=(session["email"].split('@'))[0]

        return render_template('home.html', \
        user=user, privileges=privileges, subjects= subjects)

    @app.route('/allSubjects')
    @decorators.login_required
    def allSubjects():
        # Querying database for taking the subjects that each user has access
        subjects = []
        user_id=db_session.query(models.User.id).filter_by(email=session["email"]).first()

        # If user is admin, render all subjects

        privilege_name = db_session.query(models.Privilege.name).join(models.privileges_users, Privilege.id==privileges_users.c.privilege_id)\
        .filter(privileges_users.c.user_id==user_id).all()

        for name in privilege_name:
            if name[0]=='admin':
                subjects_id=db_session.query(models.users_subjects.c.subject_id).all()
                for id in subjects_id:
                    subjects.extend(db_session.query(models.Subject).filter_by(id=id).all())
                return render_template('allSubjects.html', user=(session["email"].split('@'))[0], subjects= subjects)

        subjects_id=db_session.query(models.users_subjects.c.subject_id).filter(models.users_subjects.c.user_id==user_id).all()
        for id in subjects_id:
            subjects.extend(db_session.query(models.Subject).filter_by(id=id).all())

        return render_template('allSubjects.html', user=(session["email"].split('@'))[0], subjects= subjects)

    @app.route('/createSubject', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.privileges_required('professor')
    def createSubject():
        acronym=request.form["acronym"]
        name=request.form["name"]
        degree=request.form["degree"]
        year= request.form["year"]
        description=request.form["description"]

        if (acronym=="" or name=="" or degree=="" or year==""):
            flash('Error! Incompleted fields', 'danger')
            return redirect('/home')

        create_subject(db_session, acronym, name, degree, year, description)

        subject_id=db_session.query(models.Subject.id).\
        filter(models.Subject.acronym==acronym).filter(models.Subject.year==year).\
        filter(models.Subject.degree==degree).first()

        add_user_to_subject(db_session, engine, session["email"], subject_id, "professor")

        return redirect('/home')

    @app.route('/subject/<id>', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.privileges_required('user')
    def subject(id):
        subject=db_session.query(models.Subject).filter_by(id=id).first()
        if (subject == None):
            flash('Error! Subject does not exists', 'danger')
            return redirect('/home')

        user=(session["email"].split('@'))[0]
        privileges=get_privileges(db_session, session["email"])

        for privilege in privileges:
            if privilege.name== 'admin':
                role='admin'
                return render_template('subject.html',user=user, role=role, subject= subject)

        role=get_role_subject(db_session, session["email"], id)



        return render_template('subject.html',user=user, role=role, subject= subject)

    @app.route('/manageSubject/<id>', methods=['GET', 'POST'])
    @decorators.login_required
    # @decorators.privileges_required('professor')
    def configSubject(id):
        subject=db_session.query(models.Subject).filter_by(id=id).first()
        if (subject == None):
            flash('Error! Subject does not exists', 'danger')
            return redirect('/home')

        user=(session["email"].split('@'))[0]
        users = get_users_in_subject(db_session,id)

        users_in_subject=[]
        for i in range(len(users)):
            row = [db_session.query(User).filter(User.id==users[i][0]).first(), db_session.query(Role).filter(Role.id==users[i][1]).first()]
            users_in_subject.append(row)

        privileges=get_privileges(db_session, session["email"])

        for privilege in privileges:
            if privilege.name== 'admin':
                role='admin'
                return render_template('manageSubject.html',user=user, role=role, subject= subject, users_in_subject=users_in_subject)

        role=get_role_subject(db_session, session["email"], id)

        roles_db=db_session.query(models.Role).all()

        return render_template('manageSubject.html',user=user, role=role, subject= subject, users_in_subject=users_in_subject, roles_db=roles_db)


    @app.route('/uploadUsers', methods=['POST'])
    @decorators.login_required
    # @decorators.privileges_required('professor')
    def uploadUsers():
        subject_id = request.form['subject_id']
        if request.files['file']:
            flask_file = request.files['file']
            data = []
            stream = codecs.iterdecode(flask_file.stream, 'utf-8')
            read_file=list(csv.reader(stream, dialect=csv.excel))
            if 'EMAIL' in read_file[0]:
                email_index=read_file[0].index('EMAIL')

            for row in read_file:
                if row:
                    if row[email_index]=='EMAIL':
                        continue
                    data.append(row[email_index])
            for email in data:
                name = (email.split('@'))[0]
                user_id = db_session.query(models.User.id).filter_by(email=email).first()

                # If the user isn't in the DB, we add it
                if (user_id == None):
                    create_user(db_session, engine, name, email)

                # Taking id again in case the user didn't exist
                user_id = db_session.query(models.User.id).filter_by(email=email).first()

                #If the user is already added, continue
                if not (db_session.query(models.users_subjects).filter_by(subject_id=subject_id)\
                .filter_by(user_id=user_id).first()==None):

                    flash ("Warning! User was already added",'warning')
                    continue

                add_user_to_subject(db_session, engine, email, subject_id, request.form["role"])


            return redirect('/manageSubject/'+ subject_id)
        else:
            flash ("Error! It is not a valid input", 'danger')
            return redirect('/manageSubject/'+ subject_id)

    @app.route('/uploadUser', methods=['POST'])
    @decorators.login_required
    # @decorators.privileges_required('professor')
    def uploadUser():
        # Getting subject_id from form
        subject_id = request.form['subject_id']

        # Checking if we have email in form
        if request.form['email']:
            # Taking email, name and id
            email=request.form['email']
            name = (email.split('@'))[0]
            user_id = db_session.query(models.User.id).filter_by(email=email).first()

            # If the user isn't in the DB, we add it
            if (user_id == None):
                create_user(db_session, engine, name, email)

            # Taking id again in case the user didn't exist
            user_id = db_session.query(models.User.id).filter_by(email=email).first()

            #If the user is already added, return
            if not (db_session.query(models.users_subjects).filter_by(subject_id=subject_id).filter_by(user_id=user_id).first()==None):
                flash ("Error! User is already added in subject",'danger')
                return redirect('/subject/'+ subject_id)

            add_user_to_subject(db_session, engine, email, subject_id, "student")

            # Redirecting to same page with a success message
            flash ("Success! User added to subject",'success')
            return redirect('/manageSubject/'+ subject_id)
        else:
            # If there is not email, flash error
            flash ("Error! Empty input",'danger')
            return redirect('/manageSubject/'+ subject_id)

    @app.route('/deleteUserSubject',  methods=['GET', 'POST'])
    @decorators.login_required
    # @decorators.privileges_required('professor')
    def deleteUser():
        user_id=request.form['user_id']
        subject_id=request.form['subject_id']
        delete_user_in_subject(db_session, user_id, subject_id)

        flash ("Success! User deleted from subject",'success')
        return redirect('/manageSubject/'+ subject_id)



    @app.route('/users')
    @decorators.login_required
    @decorators.privileges_required('admin')
    def users():
        error = None
        return render_template('users.html', error=error,user=(session["email"].split('@'))[0])

    @app.route('/test')
    @decorators.login_required
    def test():
        with app.app_context():
            roles=models.Role.query.filter_by(name="superuser").all()
            id=(o.id for o in roles)
            print (next(id))

        return render_template('index.html')

    migrate = Migrate(app,db)

    return app


def init_system():
    global app
    with app.app_context():

        # Checking if table role exists, if not, return
        if not engine.dialect.has_table(engine, 'privilege'):
          return
        else:
            # Adding different core privileges
            user_privilege = models.Privilege(name='user')
            professor_privilege = models.Privilege(name='professor')
            admin_privilege = models.Privilege(name='admin')

            if (models.Privilege.query.filter_by(name='user').first()==None):
                db_session.add(user_privilege)
            if (models.Privilege.query.filter_by(name='professor').first()==None):
                db_session.add(professor_privilege)
            if (models.Privilege.query.filter_by(name='admin').first()==None):
                db_session.add(admin_privilege)

        if not engine.dialect.has_table(engine, 'role'):
          return
        else:
            # Adding roles for functions in subjects
            user_role = models.Role(name='student')
            professor_role = models.Role(name='professor')
            admin_role = models.Role(name='admin')

            if (models.Role.query.filter_by(name='user').first()==None):
                db_session.add(user_role)
            if (models.Role.query.filter_by(name='professor').first()==None):
                db_session.add(professor_role)
            if (models.Role.query.filter_by(name='admin').first()==None):
                db_session.add(admin_role)

            # Adding first user admin
            # IMPORTANT: delete after transferring admin privilege for security reasons
            if (models.User.query.filter_by(email='admin').first()==None):
                create_admin_user(db_session, engine, 'admin', 'admin')
