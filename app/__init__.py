from flask import Flask, url_for, redirect,  \
render_template, request, abort, session, flash

import csv, codecs, os, datetime, json

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
    # init_db()
    # init_system()


    # # Function of Flask-Login. User loader
    # @login_manager.user_loader
    # def load_user(email):
    #     return models.User.get(email)
    #
    # # Initialisation of Flask-Login
    # login_manager.init_app(app)
    # login_manager.login_message = 'You must be logged in to access this page'


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
        privilege=get_user_privileges(db_session, session["email"])
        session["privilege"]=privilege.name
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
        subjects_id=get_subjects_from_user(db_session, user_id)

        for id in subjects_id:
            subjects.extend(get_subject_by_year(db_session, id, current_year))

        user=(session["email"].split('@'))[0]

        return render_template('home.html', \
        user=user, privilege=session["privilege"], subjects= subjects, degrees=appconfig.degrees)

    @app.route('/allSubjects')
    @decorators.login_required
    def allSubjects():
        # Querying database for taking the subjects that each user has access
        subjects = []
        # If user is admin, render all subjects
        privilege= get_user_privileges(db_session, session["email"])

        if privilege.name == 'admin':
            subjects.extend(get_all_subjects(db_session))
            return render_template('allSubjects.html', privilege=session["privilege"],\
            user=(session["email"].split('@'))[0], subjects= subjects)

        user_id= get_user_id(db_session, session["email"])
        subjects_id= get_subjects_from_user(db_session, user_id)

        for id in subjects_id:
            subjects.append(get_subject(db_session, id))

        return render_template('allSubjects.html', privilege=session["privilege"], \
        user=(session["email"].split('@'))[0], subjects= subjects)

    @app.route('/subject/<id>', methods=['GET', 'POST'])
    @decorators.login_required
    def subject(id):
        subject=get_subject(db_session, id)
        if (subject == None):
            flash('Error! Subject does not exists', 'danger')
            return redirect('/home')

        user=(session["email"].split('@'))[0]
        practices=get_practices(db_session, id)
        privilege=get_user_privileges(db_session, session["email"])

        if privilege.name== 'admin':
            role='admin'
            session["role"]=role

            return render_template('subject.html',privilege=session["privilege"], \
            user=user, role=role, subject= subject,practices=practices, \
            rating_ways=appconfig.rating_ways,degrees=appconfig.degrees )

        role=get_role_subject(db_session, session["email"], id)
        session["role"]=role
        session["subject_id"]=id

        return render_template('subject.html',user=user, privilege=session["privilege"], \
        role=role, subject= subject, practices=practices, rating_ways=appconfig.rating_ways, degrees=appconfig.degrees)

    @app.route('/manageSubject/<id>', methods=['GET', 'POST'])
    @decorators.login_required
    def manageSubject(id):
        if not (session["privilege"]=="admin"):
            role=get_role_subject(db_session, session["email"] , id)
            if not (role=="admin" or role=="professor"):
                flash('Error! You cannot do that!', 'danger')
                return redirect('/home')

        subject= get_subject(db_session, id)

        if (subject == None):
            flash('Error! Subject does not exists', 'danger')
            return redirect('/home')

        user=(session["email"].split('@'))[0]
        users = get_users_in_subject(db_session,id)

        users_in_subject=[]

        for i in range(len(users)):
            user_in=get_user_by_id(db_session,users[i][0])
            role=get_role(db_session,users[i][1])

            group=get_group_from_user_in_subject(db_session, users[i][0], id)
            if (group != None):
                grouping=get_grouping(db_session, group.grouping_id)
            else:
                grouping=None

            row = [user_in,role, group, grouping]
            users_in_subject.append(row)

        roles_db=get_roles(db_session)
        groupings=get_groupings_subject(db_session,id)
        groupings_json=json.dumps(groupings)
        groups=get_groups_subject(db_session,id)
        groups_json=json.dumps(groups)

        if session["privilege"]== 'admin':
            role='admin'

            return render_template('manageSubject.html', privilege=session["privilege"], user=user,\
             role=role, subject= subject, users_in_subject=users_in_subject, roles_db=roles_db, \
             groupings_json=groupings_json, groups_json=groups_json, groupings=groupings, groups=groups)

        role=get_role_subject(db_session, session["email"], id)

        return render_template('manageSubject.html',user=user, privilege=session["privilege"],\
        role=role, subject= subject, users_in_subject=users_in_subject, roles_db=roles_db, \
        groupings_json=groupings_json, groups_json=groups_json, groupings=groupings, groups=groups)

    @app.route('/practice/<id>', methods=['GET', 'POST'])
    @decorators.login_required
    def practice(id):
        practice=get_practice(db_session, id)

        if (practice == None):
            flash('Error! Practice does not exists', 'danger')
            return redirect('/home')

        user=(session["email"].split('@'))[0]

        milestones=get_practice_milestones(db_session, id)
        return render_template('practice.html',user=user, privilege=session["privilege"], \
        practice=practice, role=session["role"],milestones=milestones, modes=appconfig.milestone_modes,\
        rating_ways=appconfig.rating_ways)


    @app.route('/users')
    @decorators.login_required
    @decorators.privileges_required('admin')
    def users():
        user=(session["email"].split('@'))[0]
        users = get_users_privileges(db_session)
        privileges=get_privileges(db_session)

        users_in_system=[]

        for i in range(len(users)):
            row = [get_user_by_id(db_session, users[i][0]), get_privilege(db_session,users[i][1])]
            users_in_system.append(row)

        return render_template('users.html', user=user, users=users_in_system, \
        privilege=session["privilege"], privileges=privileges)

# DB Interaction Routes _____________________________________________________________________________________________________________
    @app.route('/createUser', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.privileges_required('admin')
    def createUser():
        email=request.form["email"]
        privilege=request.form["privilege"]

        if (get_user(db_session, email)==None):
            flash('Error: User already exists', 'danger')
            return redirect('/users')

        name=email.split('@')[0]
        create_user(db_session,engine,name,email,privilege)

        return redirect('/users')

    @app.route('/createSubject', methods=['GET', 'POST'])
    @decorators.login_required
    # @decorators.privileges_required('admin', 'professor')
    def createSubject():
        acronym=request.form["acronym"]
        name=request.form["name"]
        degree=request.form["degree"]
        year= request.form["year"]
        description=request.form["description"]

        if (acronym=="" or name=="" or degree=="" or year==""):
            flash('Error! Incompleted fields', 'danger')
            return redirect('/home')

        subject= create_subject(db_session, acronym, name, degree, year, description)

        add_user_to_subject(db_session, engine, session["email"], subject.id, "admin")

        return redirect('/home')

    @app.route('/createPractice', methods=['GET', 'POST'])
    @decorators.login_required
    def createPractice():
        name=request.form["name"]
        milestones=request.form["milestones"]
        rating_way=request.form["rating_way"]
        subject_id=request.form["subject_id"]
        description=request.form["description"]

        if (name=="" or milestones=="" or rating_way==""):
            flash('Error! Incompleted fields', 'danger')
            return redirect('/subject/'+subject_id)

        create_practice(db_session,name,milestones,rating_way,subject_id, description)

        return redirect('/subject/'+subject_id)

    @app.route('/createMilestone', methods=['GET', 'POST'])
    @decorators.login_required
    def createMilestone():
        name=request.form["name"]
        mode=request.form["mode"]
        practice_id=request.form["practice_id"]
        description=request.form["description"]

        practice=get_practice(db_session, practice_id )
        milestones=get_practice_milestones(db_session,practice_id)

        if (len(milestones)>=practice.milestones):
            flash("Error! Practice has " + str(practice.milestones) +" milestone(s) and they already exist.", 'danger')
            return redirect('/practice/'+practice_id)

        if (name=="" or mode==""):
            flash('Error! Incompleted fields', 'danger')
            return redirect('/practice/'+practice_id)

        create_milestone(db_session, name, mode, practice_id, description)

        return redirect('/practice/'+practice_id)

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
            if 'email' in read_file[0]:
                email_index=read_file[0].index('email')
            if 'Email' in read_file[0]:
                email_index=read_file[0].index('Email')

            for row in read_file:
                if row:
                    if (row[email_index]=='EMAIL' or row[email_index]=='email' or row[email_index]=='Email'):
                        continue
                    data.append(row[email_index])

            for email in data:
                name = (email.split('@'))[0]
                user_id = get_user_id(db_session, email)

                # If the user isn't in the DB, we add it
                if (user_id == None):
                    create_user(db_session, engine, name, email, "user")

                # Taking id again in case the user didn't exist
                user_id = get_user_id(db_session, email)

                #If the user is already added, continue
                if (check_user_in_subject(db_session,subject_id,user_id)==True):
                    flash ("Warning! User "+ email + " was already added",'warning')
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
            user_id = get_user_id(db_session, email)

            # If the user isn't in the DB, we add it
            if (user_id == None):
                create_user(db_session, engine, name, email, "user")

            # Taking id again in case the user didn't exist
            user_id = get_user_id(db_session, email)

            #If the user is already added, return
            if (check_user_in_subject(db_session,subject_id,user_id)==True):
                flash ("Warning! User was already added",'warning')
                return redirect('/manageSubject/'+ subject_id)

            add_user_to_subject(db_session, engine, email, subject_id,  request.form["role"])

            # Redirecting to same page with a success message
            flash ("Success! User " + email +" added to subject",'success')
            return redirect('/manageSubject/'+ subject_id)
        else:
            # If there is not email, flash error
            flash ("Error! Empty input",'danger')
            return redirect('/manageSubject/'+ subject_id)

    @app.route('/updateSubject', methods=['GET', 'POST'])
    @decorators.login_required
    # @decorators.privileges_required('admin', 'professor')
    def updateSubject():
        id=request.form["id"]
        acronym=request.form["acronym"]
        name=request.form["name"]
        degree=request.form["degree"]
        year= request.form["year"]
        description=request.form["description"]

        if (acronym=="" or name=="" or degree=="" or year==""):
            flash('Error! Incompleted fields', 'danger')
            return redirect('/subject/'+ id)

        update_subject(db_session,id, acronym, name, degree, year, description)

        return redirect('/subject/'+id)

    @app.route('/updateUserGroup', methods=['GET', 'POST'])
    @decorators.login_required
    # @decorators.privileges_required('admin', 'professor')
    def updateuserGroup():
        email=request.form["email"]
        subject_id=request.form["subject_id"]
        group_id=request.form["selectGroups"]

        print(group_id )
        print (email )

        user_id=get_user_id(db_session, email)

        print(user_id )



        if (group_id==""):
            flash('Error! Incompleted fields', 'danger')
            return redirect('/manageSubject/'+ subject_id)

        update_user_group(db_session, group_id, user_id[0])

        return redirect('/manageSubject/'+subject_id)

    @app.route('/createGrouping', methods=['POST'])
    @decorators.login_required
    def createGrouping():
        name=request.form["name"]
        subject_id = request.form['subject_id']

        if (name==""):
            flash ("Error! Empty input",'danger')
            return redirect('/manageSubject/'+ subject_id)

        add_grouping_subject(engine, name, subject_id)

        flash ("Success! Grouping " + name +" added to subject",'success')
        return redirect('/manageSubject/'+ subject_id)

    @app.route('/createGroup', methods=['POST'])
    @decorators.login_required
    def createGroup():
        name=request.form["name"]
        grouping_id = request.form['grouping_id']
        subject_id=request.form['subject_id']

        if (name==""):
            flash ("Error! Empty input",'danger')
            return redirect('/manageSubject/'+ subject_id)

        add_group_subject(engine, name, grouping_id)

        flash ("Success! Group " + name +" added to subject",'success')
        return redirect('/manageSubject/'+ subject_id)


    @app.route('/updatePractice', methods=['GET', 'POST'])
    @decorators.login_required
    def updatePractice():
        id=request.form["practice_id"]
        name=request.form["name"]
        milestones=request.form["milestones"]
        rating_way=request.form["rating_way"]
        description=request.form["description"]
        subject_id=request.form["subject_id"]

        if (name=="" or milestones=="" or rating_way==""):
            flash('Error! Incompleted fields', 'danger')
            return redirect('/practice/'+id)

        update_practice(db_session,id,name,milestones,rating_way,subject_id, description)

        return redirect('/practice/'+id)

    @app.route('/changePrivilege', methods=['GET', 'POST'])
    @decorators.login_required
    @decorators.privileges_required('admin')
    def changePrivilege():
        privilege=request.form['privilege']
        email=request.form['email']

        update_privilege(db_session, email, privilege)

        flash ("Success! You changed the privilege of " + email + " to " + privilege ,'success')
        return redirect('/users')

    @app.route('/changeRole', methods=['GET', 'POST'])
    @decorators.login_required
    def changeRole():
        role=request.form['role']
        email=request.form['email']
        subject_id=request.form['subject_id']

        update_role(db_session, email, role, subject_id)

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


        if not (session["privilege"]=="admin"):
            flash('Error! You cannot do that!', 'danger')
            return redirect('/home')

        delete_user(db_session,user_id)

        flash ("Success! User deleted from system",'success')
        return redirect('/users')


    @app.route('/deletePractice/<id>', methods=['GET','POST'])
    @decorators.login_required
    def deletePractice(id):
        subject_id= get_subject_id_practice(db_session, id)
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

            if (models.Role.query.filter_by(name='student').first()==None):
                db_session.add(user_role)
            if (models.Role.query.filter_by(name='professor').first()==None):
                db_session.add(professor_role)
            if (models.Role.query.filter_by(name='admin').first()==None):
                db_session.add(admin_role)

            # Adding first user admin
            # IMPORTANT: delete after transferring admin privilege for security reasons
            if (models.User.query.filter_by(email='admin').first()==None):
                create_user(db_session, engine, 'admin', 'admin', 'admin')
