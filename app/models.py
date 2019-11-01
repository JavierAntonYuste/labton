from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from app.db_init import Base
from sqlalchemy.orm import relationship, backref

users_subjects = Table(
    'users_subjects',
     Base.metadata,
    Column('subject_id', Integer(), ForeignKey('subjects.id'),primary_key=True),
    Column('user_id', Integer(), ForeignKey('user.id'),primary_key=True),
    Column('role_id', ForeignKey('role.id'))
)

privileges_users = Table(
    'privileges_users',
     Base.metadata,
    Column('user_id', Integer(), ForeignKey('user.id')),
    Column('privilege_id', Integer(), ForeignKey('privilege.id'))
)

class Role(Base):

    __tablename__= 'role'

    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    def __str__(self):
        return self.name

class Privilege(Base):

    __tablename__= 'privilege'

    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    def __str__(self):
        return self.name


class User(Base):

    __tablename__= 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    email = Column(String(255), unique=True)
    privileges = relationship('Privilege', secondary=privileges_users,
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
