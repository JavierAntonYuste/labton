from app.models import *

def create_user(db_session, engine, name, email):
    user=User(first_name=name,email= email)
    db_session.add(user)
    db_session.commit()

    try:
        con = engine.connect()
        trans = con.begin()
        user_id = db_session.query(User.id).filter_by(email=email).first()
        role_id = db_session.query(Role.id).filter_by(name='user').first()

        # Creating relations
        con.execute(roles_users.insert().values(
            user_id=user_id,
            role_id= role_id
            ))

        trans.commit()

    except:
        trans.rollback()
        raise

    con.close()

    return

def create_admin_user(db_session, engine, name, email):
    user=User(first_name=name,email= email)
    db_session.add(user)
    db_session.commit()

    try:
        con = engine.connect()
        trans = con.begin()
        user_id = db_session.query(User.id).filter_by(email=email).first()
        role_id = db_session.query(Role.id).filter_by(name='user').first()
        admin_role_id = db_session.query(Role.id).filter_by(name='admin').first()

        # Creating relations
        con.execute(roles_users.insert().values(
            user_id=user_id,
            role_id= role_id
            ))

        con.execute(roles_users.insert().values(
            user_id=user_id,
            role_id= admin_role_id
            ))

        trans.commit()

    except:
        trans.rollback()
        raise

    con.close()

    return

def get_role_subject(db_session, email, id):
    role=(db_session.query(Role.name).\
    join(users_subjects, Role.id==users_subjects.c.role_id).join(User, users_subjects.c.user_id==User.id).\
    filter(User.email==email).filter(users_subjects.c.subject_id==id).first())[0]

    return role

def get_users_in_subject (db_session, subject_id ):
    users=db_session.query(User)\
    .join(users_subjects,User.id==users_subjects.c.user_id).join(Subject, users_subjects.c.subject_id==Subject.id)\
    .filter(Subject.id==subject_id)

    return users
