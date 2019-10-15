from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user

from flask_security.utils import encrypt_password

from app import db


users_subjects= roles_users = db.Table(
    'users_subjects',
    db.Column('subject_id', db.Integer(), db.ForeignKey('subjects.id')),
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model, RoleMixin):

    # __tablename__= 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):

    # __tablename__= 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

    def get (user_id):
        return User.query.filter_by(id=user_id).first()


class Subject(db.Model):
    """
    Create a table for subjects
    """
    __tablename__= 'subjects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    acronym = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String (100), nullable = False)
    year = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String(1000))
    degree = db.Column(db.String(100), nullable=False)
    users = db.relationship('User', secondary=users_subjects,
                            backref=db.backref('subjects', lazy='dynamic'))

    def __init__(self, id, name):
        self.id=id
        self.name=name
