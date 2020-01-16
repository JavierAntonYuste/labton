import os

#SECRET_KEY = 'p9Bv<3Eid9%$i01'
SECRET_KEY = os.urandom(12)
SQLALCHEMY_DATABASE_URI = 'mysql://labton:labton@db/labton'

# Create in-memory database
SQLALCHEMY_ECHO = True
