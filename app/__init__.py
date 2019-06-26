from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user

from flask_security.utils import encrypt_password
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, expose


from sqlalchemy import create_engine
from sqlalchemy.event import listens_for, listen
from sqlalchemy.event import listen
from sqlalchemy.orm import sessionmaker

from instance import config

from config import app_config
from app import views



db = SQLAlchemy()
engine= create_engine(config.SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()


login_manager = LoginManager()


def create_app(config_name):
    global app
    app = Flask(__name__, instance_relative_config=True)

    #app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from app import models

    # Setup Flask-Security
    global user_datastore
    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
    security = Security(app, user_datastore)


    db.init_app(app)
    init_system()

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.get(user_id)

    login_manager.init_app(app)
    login_manager.login_message = 'You must be logged in to access this page'
    login_manager.login_view = 'auth.login' #Cambiar cuando se haga la pantalla de login

    # Rutas
    @app.route('/')
    def root_directory():
        # return render_template('security/login_user.html')
        return render_template('index.html')

    @app.route('/admin')
    def admin():

        return render_template('admin.html')


    # Create admin
    admin = flask_admin.Admin(
        app,
        'My Dashboard',
        base_template='my_master.html',
        template_mode='bootstrap3',
    )

    # Add model views
    admin.add_view(views.MyModelView(models.Role, db.session, menu_icon_type='fa', menu_icon_value='fa-server', name="Roles"))
    admin.add_view(views.UserView(models.User, db.session, menu_icon_type='fa', menu_icon_value='fa-users', name="Users"))
    admin.add_view(views.CustomView(name="Custom view", endpoint='custom', menu_icon_type='fa', menu_icon_value='fa-connectdevelop',))

    # define a context processor for merging flask-admin's template context into the
    # flask-security views.
    @security.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for
        )

    @app.route('/hello/')
    @app.route('/hello/<name>')
    def hello(name=None):
        return render_template('index.html', name=name)

    migrate = Migrate(app,db)

    return app

def init_system():
    global app
    with app.app_context():

        # if not engine.dialect.has_table(engine, 'profesores'):
        #     return
        # else:
        #     if (models.Profesor.query.filter_by(name='root').first()==None):
        #         me = models.Profesor('root', 'noMail')
        #         me.set_password('root')
        #
        #         db.session.add(me)
        #         db.session.commit()

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
                    password=encrypt_password('admin'),
                    roles=[user_role, super_user_role]
                )

            db.session.commit()
