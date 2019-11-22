from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from app.db_init import Base
from sqlalchemy.orm import relationship, backref

users_subjects = Table(
    'users_subjects',
     Base.metadata,
    Column('subject_id', Integer(), ForeignKey('subjects.id'),primary_key=True),
    Column('user_id', Integer(), ForeignKey('user.id'),primary_key=True),
    Column('role_id', ForeignKey('role.id'), nullable=False)
)

privileges_users = Table(
    'privileges_users',
     Base.metadata,
    Column('user_id', Integer(), ForeignKey('user.id'), primary_key=True),
    Column('privilege_id', Integer(), ForeignKey('privilege.id'))
)

groupings_subject = Table(
    'groupings_subject',
     Base.metadata,
    Column('grouping_id', Integer(),primary_key=True, autoincrement=True),
    Column('name', String(80), nullable=False),
    Column('subject_id', ForeignKey('subjects.id'), nullable=False)
)

groups_subject = Table(
    'groups_subject',
     Base.metadata,
    Column('group_id', Integer(),primary_key=True, autoincrement=True),
    Column('name', String(80), nullable=False),
    Column('grouping_id', ForeignKey('groupings_subject.grouping_id'), nullable=False),
)

users_group_subject = Table(
    'users_group_subject',
     Base.metadata,
    Column('group_id', ForeignKey('groups_subject.group_id'), nullable=False),
    Column('user_id', ForeignKey('user.id'), nullable=False)
    )

# Uncomment when session model is done

# groupings_session = Table(
#     'groupings_session',
#      Base.metadata,
#     Column('grouping_id', Integer(),primary_key=True, autoincrement=True),
#     Column('name', String(80), nullable=False),
#     Column('session_id', ForeignKey('session.id'), nullable=False)
# )
#
# groups_session= Table(
#     'groups_session',
#      Base.metadata,
#     Column('group_id', Integer(),primary_key=True, autoincrement=True),
#     Column('grouping_id', ForeignKey(groupings_subject.grouping_id), nullable=False),
#     Column('user_id', ForeignKey('user.id'), nullable=False)
# )
# users_group_session = Table(
#     'users_group_session',
#      Base.metadata,
#     Column('group_id', ForeignKey(groups_session.group_id), nullable=False),
#     Column('user_id', ForeignKey(user.id), nullable=False)
#     )


class Role(Base):

    __tablename__= 'role'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(String(255))


class Privilege(Base):

    __tablename__= 'privilege'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True, nullable=False)
    description = Column(String(255))


class User(Base):

    __tablename__= 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    privileges = relationship('Privilege', secondary=privileges_users,
                            backref=backref('users', lazy='dynamic'))


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


class Practice(Base):

    __tablename__= 'practices'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    milestones= Column(Integer(), nullable=False)
    rating_way= Column(String(80), nullable=False)
    subject_id=Column(Integer(), ForeignKey("subjects.id"), nullable=False)
    description = Column(String(255))


class Milestone(Base):

    __tablename__= 'milestones'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(80), nullable=False)
    mode= Column(String(80), nullable=False)
    practice_id=Column(Integer(), ForeignKey("practices.id"), nullable=False)
    description = Column(String(255))
