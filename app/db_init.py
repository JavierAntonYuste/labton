from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from instance import config


""" Initialisation of the database and its session.

Created apart for not making interdependencies among several scripts.
"""
## TODO see singleton, if that is necessary or not
db = SQLAlchemy()
engine= create_engine(config.SQLALCHEMY_DATABASE_URI)
DB_Session = sessionmaker(bind=engine)
db_session = DB_Session()
