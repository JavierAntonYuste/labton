from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from app.db_init import Base
from sqlalchemy.orm import relationship, backref

#TODO in this table, there must be only one entre per user and subject!! PRIMARY KEY= user_id+subject_id?
users_subjects= roles_users = Table(
    'users_subjects',
     Base.metadata,
    Column('subject_id', Integer(), ForeignKey('subjects.id'),primary_key=True),
    Column('user_id', Integer(), ForeignKey('user.id'),primary_key=True),
    Column('role_id', Integer(), ForeignKey('role.id')),
)

roles_users = Table(
    'roles_users',
     Base.metadata,
    Column('user_id', Integer(), ForeignKey('user.id')),
    Column('role_id', Integer(), ForeignKey('role.id'))
)

class Role(Base):

    __tablename__= 'role'

    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    def __str__(self):
        return self.name


class User(Base):

    __tablename__= 'user'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary=roles_users,
                            backref=backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email

    def get (user_id):
        return User.query.filter_by(id=user_id).first()


class Subject(Base):
    """
    Create a table for subjects
    """
    __tablename__= 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    acronym = Column(String(10), nullable=False)
    name = Column(String (100), nullable = False)
    year = Column(Integer, nullable = False)
    description = Column(String(1000))
    degree = Column(String(100), nullable=False)
    users = relationship('User', secondary=users_subjects,
                            backref=backref('subjects', lazy='dynamic'))

    def __init__(self, id, name):
        self.id=id
        self.name=name
