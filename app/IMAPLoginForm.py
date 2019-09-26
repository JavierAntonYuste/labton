from flask_security.forms import LoginForm
import imaplib, sys

from flask_security import SQLAlchemyUserDatastore

from app import db, models, session, appconfig

class IMAPLoginForm(LoginForm):
    def validate(self):
        form=LoginForm()
        response= False

        email=form.email.data
        passwd=form.password.data

        if email=='admin':
            if (models.User.query.filter_by(email='admin').first()==None):
                response=False
                super(IMAPLoginForm, self).validate()
                return response
            else:
                response=True
                super(IMAPLoginForm, self).validate()
                return response

        if not '@' in email:
            response= False
            super(IMAPLoginForm, self).validate()
            return response

        user=(email.split('@'))[0]
        server= (email.split('@'))[1]



        ## Seleccion del servidor IMAP
        def mail_server(server):
            return appconfig.IMAP_servers.get(server)

        IMAP_server = mail_server(server)

        if (IMAP_server==None):
            response= False
            super(IMAPLoginForm, self).validate()
            return response

        imap = imaplib.IMAP4_SSL(IMAP_server, port=993)

        try:
            status, summary = imap.login(user, passwd)
            if status == "OK":
                ## Si el usuario no esta, una vez que se comprueba que esta bien, lo mete en la BBDD
                user_role = models.Role(name='user')

                if (models.User.query.filter_by(email=email).first()==None):
                    user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
                    new_user = user_datastore.create_user(
                        first_name=user,
                        email=email,
                        roles=[user_role]
                        )

                    db.session.commit()
                response=True

        except imaplib.IMAP4.error:
            print("Error logging into Mail")
            sys.exit(0)  # Successful termination

        # Logout of the IMAP server
        imap.logout()

        super(IMAPLoginForm, self).validate()

        return response
