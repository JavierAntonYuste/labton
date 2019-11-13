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
from app import decorators, appconfig
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

# View Routes ______________________________________________________________________________________________
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

        subjects_id=db_session.query(models.users_subjects.c.subject_id).filter(models.users_subjects.c.user_id==user_id).all()
        for id in subjects_id:
            subjects.extend(db_session.query(models.Subject).filter_by(id=id,year=current_year).all())

        user=(session["email"].split('@'))[0]

        return render_template('home.html', \
        user=user, privileges=privileges, subjects= subjects, degrees=appconfig.degrees)

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
                subjects.extend(db_session.query(models.Subject).all())
                return render_template('allSubjects.html', user=(session["email"].split('@'))[0], subjects= subjects)

        subjects_id=db_session.query(models.users_subjects.c.subject_id).filter(models.users_subjects.c.user_id==user_id).all()
        for id in subjects_id:
            subjects.extend(db_session.query(models.Subject).filter_by(id=id).all())

        return render_template('allSubjects.html', user=(session["email"].split('@'))[0], subjects= subjects)

    @app.route('/subject/<id>', methods=['GET', 'POST'])
    @decorators.login_required
    def subject(id):
        subject=db_session.query(models.Subject).filter_by(id=id).first()
        if (subject == None):
            flash('Error! Subject does not exists', 'danger')
            return redirect('/home')

        user=(session["email"].split('@'))[0]
        practices=get_practices(db_session, id)
        privileges=get_privileges(db_session, session["email"])


        for privilege in privileges:
            if privilege.name== 'admin':
                role='admin'
                session["role"]=role

                return render_template('subject.html',user=user, role=role, subject= subject,practices=practices, rating_ways=appconfig.rating_ways)

        role=get_role_subject(db_session, session["email"], id)
        session["role"]=role
        session["subject_id"]=id


        return render_template('subject.html',user=user, role=role, subject= subject, practices=practices, rating_ways=appconfig.rating_ways)

    @app.route('/manageSubject/<id>', methods=['GET', 'POST'])
    @decorators.login_required
    def configSubject(id):
        role=get_role_subject(db_session, session["email"] , id)
        if not (role=="admin" or role=="professor"):
            flash('Error! You cannot do that!', 'danger')
            return redirect('/home')

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
        roles_db=db_session.query(models.Role).all()

        for privilege in privileges:
            if privilege.name== 'admin':
                role='admin'
                return render_template('manageSubject.html',user=user, role=role, subject= subject, users_in_subject=users_in_subject, roles_db=roles_db)

        role=get_role_subject(db_session, session["email"], id)
        return render_template('manageSubject.html',user=user, role=role, subject= subject, users_in_subject=users_in_subject, roles_db=roles_db)

    @app.route('/practice/<id>', methods=['GET', 'POST'])
    @decorators.login_required
    def practice(id):
        practice=db_session.query(models.Practice).filter_by(id=id).first()
        if (practice == None):
            flash('Error! Practice does not exists', 'danger')
            return redirect('/home')

        user=(session["email"].split('@'))[0]
        return render_template('practice.html',user=user, practice=practice, role=session["role"])


    @app.route('/users')
    @decorators.login_required
    @decorators.privileges_required('admin')
    def users():
        user=(session["email"].split('@'))[0]
        users = get_users(db_session)
        privileges=db_session.query(Privilege).all()

        users_in_system=[]

        for i in range(len(users)):
            row = [db_session.query(User).filter(User.id==users[i][0]).first(), db_session.query(Privilege).filter(Privilege.id==users[i][1]).first()]
            users_in_system.append(row)

        return render_template('users.html', user=user, users=users_in_system, privileges=privileges)

# DB Interaction Routes _____________________________________________________________________________________________________________
    @app.route('/createUser', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.privileges_required('admin')
    def createUser():
        email=request.form["email"]
        privilege=request.form["privilege"]

        if (db_session.query(User).filter(User.email==email)==None):
            flash('Error: User already exists', 'danger')
            return redirect('/users')

        name=email.split('@')[0]
        create_user(db_session,engine,name,email,privilege)

        return redirect('/users')

    @app.route('/createSubject', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.privileges_required('admin', 'professor')
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

        add_user_to_subject(db_session, engine, session["email"], subject_id, "admin")

        return redirect('/home')

    @app.route('/createPractice', methods=['GET', 'POST'])
    @decorators.login_required
    def createPractice():
        name=request.form["name"]
        milestones=request.form["milestones"]
        rating_way=request.form["rating_way"]
        subject_id=request.form["subject_id"]
        description=request.form["description"]

        create_practice(db_session,name,milestones,rating_way,subject_id, description)

        return redirect('/subject/'+subject_id)

    @app.route('/uploadUsers', methods=['POST'])
    @decorators.login_required
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
                    create_user(db_session, engine, name, email, "user")

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
                create_user(db_session, engine, name, email, "user")

            # Taking id again in case the user didn't exist
            user_id = db_session.query(models.User.id).filter_by(email=email).first()

            #If the user is already added, return
            if not (db_session.query(models.users_subjects).filter_by(subject_id=subject_id).filter_by(user_id=user_id).first()==None):
                flash ("Warning! User was already added",'warning')
                return redirect('/manageSubject/'+ subject_id)

            add_user_to_subject(db_session, engine, email, subject_id,  request.form["role"])

            # Redirecting to same page with a success message
            flash ("Success! User added to subject",'success')
            return redirect('/manageSubject/'+ subject_id)
        else:
            # If there is not email, flash error
            flash ("Error! Empty input",'danger')
            return redirect('/manageSubject/'+ subject_id)

    @app.route('/changePrivilege', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.privileges_required('admin')
    def changePrivilege():
        privilege=request.form['privilege']
        email=request.form['email']

        change_privilege(db_session, email, privilege)

        flash ("Success! You changed the privilege of " + email + " to " + privilege ,'success')
        return redirect('/users')

    @app.route('/changeRole', methods=['GET', 'POST'])
    @decorators.login_required
    def changeRole():
        role=request.form['role']
        email=request.form['email']
        subject_id=request.form['subject_id']

        change_role(db_session, email, role, subject_id)

        flash ("Success! You changed the role of " + email + " to " + role ,'success')

        return redirect('/manageSubject/'+ subject_id)

    @app.route('/deleteUserSubject',  methods=['GET', 'POST'])
    @decorators.login_required
    def deleteUserSubject():

        if not (session["role"]=="admin" or session["role"]=="professor"):
            flash('Error! You cannot do that!', 'danger')
            return redirect('/home')

        user_id=request.form['user_id']
        subject_id=request.form['subject_id']

        delete_user_in_subject(db_session, user_id, subject_id)

        flash ("Success! User deleted from subject",'success')
        return redirect('/manageSubject/'+ subject_id)

    @app.route('/deleteSubject/<id>', methods=['GET','POST'])
    @decorators.login_required
    def deleteSubject(id):
        role=get_role_subject(db_session, session["email"] , id)
        if not (role=="admin"):
            flash('Error! You cannot do that!', 'danger')
            return redirect('/home')

        delete_subject(db_session, id)

        return redirect('/home')

    @app.route('/deleteUser', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.privileges_required('admin')
    def deleteUser():
        user_id=request.form['user_id']
        privilege= get_privileges(db_session,db_session.query(models.User.email).filter_by(id=user_id).first())
        if not (privilege=="admin"):
            flash('Error! You cannot do that!', 'danger')
            return redirect('/home')

        delete_user(db_session,user_id)

        flash ("Success! User deleted from system",'success')
        return redirect('/users')


    @app.route('/deletePractice/<id>', methods=['GET','POST'])
    @decorators.login_required
    def deletePractice(id):
        subject_id= db_session.query(models.Practice.subject_id).filter_by(id=id).first()
        role=get_role_subject(db_session, session["email"] , subject_id)

        if not (role=="admin"):
            flash('Error! You cannot do that!', 'danger')
            return redirect('/home')

        delete_practice(db_session, id)

        return redirect('/subject/'+session["subject_id"])

# End of routes ______________________________________________________________________________


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
