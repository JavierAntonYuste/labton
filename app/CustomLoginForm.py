from flask_security.forms import LoginForm
import imaplib, sys
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from app import db, models, session

IMAP_server = "correo.alumnos.upm.es"

class CustomLoginForm(LoginForm):
    def validate(self):
        form=LoginForm()
        response= False

        email=form.email.data
        passwd=form.password.data

        #Query para ver que usuarios hay;
        # Ahora hay que:
        #   1. ver que usuarios hay
        #   2. ver si el usuario esta en la BBDD
        #   3. Si no esta, meterle, si si continuar

        admin = models.User.query.filter_by(email='admin').first()
        print (admin.email)

        if email=='admin':
            response=True
            super(CustomLoginForm, self).validate()
            return response

        if not '@' in email:
            response= False
            super(CustomLoginForm, self).validate()
            return response


        server= (email.split('@'))[1] ##Hay que hacer un switch case para esto con el correo de alumnos y el de profes
        user=(email.split('@'))[0]

        imap = imaplib.IMAP4_SSL(IMAP_server, port=993)


        try:
            status, summary = imap.login(user, passwd)
            print(status)
            if status == "OK":
                print(summary)
                response=True

        except imaplib.IMAP4.error:
            print("Error logging into Mail")
            sys.exit(0)  # Successful termination

        # Logout of the IMAP server
        imap.logout()
        
        super(CustomLoginForm, self).validate()

        return response
