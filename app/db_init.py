# from sqlalchemy import *
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from instance import config
#
#
#
#
# engine= create_engine(config.SQLALCHEMY_DATABASE_URI)
# DB_Session = sessionmaker(bind=engine)
# db_session = DB_Session()

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from instance import config

 """ Initialisation of the database and its session.
 Created apart for not making interdependencies among several scripts.
 """

db = SQLAlchemy()
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import app.models
    Base.metadata.create_all(bind=engine)
