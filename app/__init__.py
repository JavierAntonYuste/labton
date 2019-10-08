from flask import Flask, url_for, redirect, render_template, request, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.utils import encrypt_password

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from instance import config

from app import views

from flask_sslify import SSLify

from functools import wraps



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

    # @login_manager.user_loader
    # def load_user(user_id):
    #     return models.User.get(user_id)
    #
    # login_manager.init_app(app)
    # login_manager.login_message = 'You must be logged in to access this page'
    # login_manager.login_view = 'auth.login' #Cambiar cuando se haga la pantalla de login


    # Routes
    @app.route('/')
    def root_directory():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':

            response=IMAPLogin.IMAPLogin(request.form['email'], request.form['password'])
            if (response==False):
                error = 'Invalid Credentials. Please try again.'
            else:
                session['logged_in'] = True
                return redirect('/')

        return render_template('login.html', error=error)

    @login_required
    @app.route('/test')
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


## Decorators
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect("login")

    return wrap

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
                superuser_id=models.Role.query.filter_by(name="superuser").all()
                id=(o.id for o in superuser_id)

                if (session.query(models.roles_users).filter(models.roles_users.c.role_id==next(id)).first()==None):
                    global user_datastore
                    test_user = user_datastore.create_user(
                        first_name='Admin',
                        email='admin',
                        password=encrypt_password('admin'),
                        roles=[user_role, super_user_role]
                    )

            db.session.commit()
