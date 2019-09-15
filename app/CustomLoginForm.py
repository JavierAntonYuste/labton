from flask_security.forms import LoginForm
import imaplib, sys
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from flask_login import current_user


IMAP_server = "correo.alumnos.upm.es"
mail_id = ""
pwd = ""



class CustomLoginForm(LoginForm):
    def validate(self):
        form=LoginForm()
        response= False

        email=form.email.data
        passwd=form.email.data

        if email=='admin':
            response=True
            super(CustomLoginForm, self).validate()
            return response

        if not '@' in email:
            return response


        server= (email.split('@'))[1] ##Hay que hacer un switch case para esto con el correo de alumnos y el de profes
        user=(email.split('@'))[0]

        print('email:' + mail_id)
        print('pwd:' + passwd)
        # print('typeof pwd: '+ str(type(passwd)))
        print('user:' + mail_id)
        print('IMAP_server:' + IMAP_server)


        imap = imaplib.IMAP4_SSL(IMAP_server, port=993)


        try:
            status, summary = imap.login(mail_id, pwd)
            print(status)
            if status == "OK":
                print(summary)
                response=True

        except imaplib.IMAP4.error:
            print("Error logging into Mail")
            sys.exit(0)  # Successful termination

        # Logout of the IMAP server
        imap.logout()




        response= True

        super(CustomLoginForm, self).validate()


        # Put code here if you want to do stuff after login attempt
        # setattr(CustomLoginForm, 'user', 'admin')

        return response
