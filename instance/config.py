import os

#SECRET_KEY = 'p9Bv<3Eid9%$i01'
SECRET_KEY = os.urandom(12)
SQLALCHEMY_DATABASE_URI = 'mysql://javi-anton:Janyu97@db/tfg_db'

# Create in-memory database
SQLALCHEMY_ECHO = True
