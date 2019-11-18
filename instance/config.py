import os

#SECRET_KEY = 'p9Bv<3Eid9%$i01'
SECRET_KEY = os.urandom(12)
SQLALCHEMY_DATABASE_URI = 'Your DB URI'

# Create in-memory database
SQLALCHEMY_ECHO = True

# Flask-Security config
# SECURITY_URL_PREFIX = "/"
# SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
# SECURITY_PASSWORD_SALT = "ATGUOHAELKiubahiughaerGOJAEGj"

# Flask-Security URLs, overridden because they don't put a / at the end
# SECURITY_LOGIN_URL = "/login/"
# SECURITY_LOGOUT_URL = "/logout/"
# SECURITY_REGISTER_URL = "/register/"
#
# SECURITY_POST_LOGIN_VIEW = "/"
# SECURITY_POST_LOGOUT_VIEW = "/"
# SECURITY_POST_REGISTER_VIEW = "/"

# Flask-Security features
# SECURITY_REGISTERABLE = True
# SECURITY_SEND_REGISTER_EMAIL = False
# SQLALCHEMY_TRACK_MODIFICATIONS = False
