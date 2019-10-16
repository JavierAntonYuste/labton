from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user

from flask_security.utils import encrypt_password

from app import db_init

# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from instance import config
# db = SQLAlchemy()
# engine= create_engine(config.SQLALCHEMY_DATABASE_URI)
# DB_Session = sessionmaker(bind=engine)
# db_session = DB_Session()


users_subjects= roles_users = db_init.db.Table(
    'users_subjects',
    db_init.db.Column('subject_id', db_init.db.Integer(), db_init.db.ForeignKey('subjects.id')),
    db_init.db.Column('user_id', db_init.db.Integer(), db_init.db.ForeignKey('user.id')),
    db_init.db.Column('role_id', db_init.db.Integer(), db_init.db.ForeignKey('role.id'))
)

roles_users = db_init.db.Table(
    'roles_users',
    db_init.db.Column('user_id', db_init.db.Integer(), db_init.db.ForeignKey('user.id')),
    db_init.db.Column('role_id', db_init.db.Integer(), db_init.db.ForeignKey('role.id'))
)

class Role(db_init.db.Model, RoleMixin):

    # __tablename__= 'roles'

    id = db_init.db.Column(db_init.db.Integer(), primary_key=True)
    name = db_init.db.Column(db_init.db.String(80), unique=True)
    description = db_init.db.Column(db_init.db.String(255))

    def __str__(self):
        return self.name


class User(db_init.db.Model, UserMixin):

    # __tablename__= 'users'

    id = db_init.db.Column(db_init.db.Integer, primary_key=True)
    first_name = db_init.db.Column(db_init.db.String(255))
    last_name = db_init.db.Column(db_init.db.String(255))
    email = db_init.db.Column(db_init.db.String(255), unique=True)
    password = db_init.db.Column(db_init.db.String(255))
    active = db_init.db.Column(db_init.db.Boolean())
    confirmed_at = db_init.db.Column(db_init.db.DateTime())
    roles = db_init.db.relationship('Role', secondary=roles_users,
                            backref=db_init.db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

    def get (user_id):
        return User.query.filter_by(id=user_id).first()


class Subject(db_init.db.Model):
    """
    Create a table for subjects
    """
    __tablename__= 'subjects'

    id = db_init.db.Column(db_init.db.Integer, primary_key=True, autoincrement=True)
    acronym = db_init.db.Column(db_init.db.String(10), nullable=False)
    name = db_init.db.Column(db_init.db.String (100), nullable = False)
    year = db_init.db.Column(db_init.db.Integer, nullable = False)
    description = db_init.db.Column(db_init.db.String(1000))
    degree = db_init.db.Column(db_init.db.String(100), nullable=False)
    users = db_init.db.relationship('User', secondary=users_subjects,
                            backref=db_init.db.backref('subjects', lazy='dynamic'))

    def __init__(self, id, name):
        self.id=id
        self.name=name
