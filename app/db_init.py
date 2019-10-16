from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from instance import config


db = SQLAlchemy()
engine= create_engine(config.SQLALCHEMY_DATABASE_URI)
DB_Session = sessionmaker(bind=engine)
db_session = DB_Session()
