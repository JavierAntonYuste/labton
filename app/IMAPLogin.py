import imaplib, sys
from flask_security import SQLAlchemyUserDatastore
from app import models, appconfig, db_init


## IMAP server selection
def mail_server(server):
    return appconfig.IMAP_servers.get(server)

## IMAP Login Procedur
def IMAPLogin(email, password):
    response= False

    ## If there is an admin user, returns True
    if email=='admin':
        if(models.User.query.filter_by(email='admin').first()==None):
            return response
        else:
            response=True
            return response

    ## If there is not a complete email address, returns False
    if not '@' in email:
        return response

    user=email.split('@')[0]
    server=email.split('@')[1]

    IMAP_server = mail_server(server)

    if (IMAP_server==None):
        return response

    imap = imaplib.IMAP4_SSL(IMAP_server, port=993)

    try:
        status, summary = imap.login(user, password)
        if status == "OK":
            ## Si el usuario no esta, una vez que se comprueba que esta bien, lo mete en la BBDD
            user_role = models.Role(name='user')

            if (models.User.query.filter_by(email=email).first()==None):
                user_datastore = SQLAlchemyUserDatastore(db_init.db, models.User, models.Role)
                new_user = user_datastore.create_user(
                    first_name=user,
                    email=email,
                    roles=[user_role]
                )

                db_init.db.session.commit()

            response=True

    except imaplib.IMAP4.error:
        print("Error logging into Mail")
        sys.exit(0)  # Fail termination

    # Logout of the IMAP server
    imap.logout()
    return response
