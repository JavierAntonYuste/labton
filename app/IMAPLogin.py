import imaplib, sys
# from flask_security import SQLAlchemyUserDatastore
from app import models, appconfig
from app.db_interactions import create_user



## IMAP server selection
def mail_server(server):
    return appconfig.IMAP_servers.get(server)

## IMAP Login Procedur
def IMAPLogin(db_session, engine, email, password):
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

            if (models.User.query.filter_by(email=email).first()==None):
                create_user(db_session,engine, user,email, "user")

            response=True
        else:
            return response
    except imaplib.IMAP4.error:
        print("Error logging into Mail")
        return response  # Fail termination

    # Logout of the IMAP server
    imap.logout()
    return response
