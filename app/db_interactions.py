from app.models import *

def create_user(db_session, engine, name, email):
    user=User(username=name,email= email)
    db_session.add(user)
    db_session.commit()

    try:
        con = engine.connect()
        trans = con.begin()
        user_id = db_session.query(User.id).filter_by(email=email).first()
        privilege_id = db_session.query(Privilege.id).filter_by(name='user').first()

        # Creating relations
        con.execute(privileges_users.insert().values(
            user_id=user_id,
            privilege_id= privilege_id
            ))

        trans.commit()

    except:
        trans.rollback()
        raise

    con.close()

    return

def create_admin_user(db_session, engine, name, email):
    user=User(username=name,email= email)
    db_session.add(user)
    db_session.commit()

    try:
        con = engine.connect()
        trans = con.begin()
        user_id = db_session.query(User.id).filter_by(email=email).first()
        privilege_id = db_session.query(Privilege.id).filter_by(name='user').first()
        admin_privilege_id = db_session.query(Privilege.id).filter_by(name='admin').first()

        # Creating relations
        con.execute(privileges_users.insert().values(
            user_id=user_id,
            privilege_id= privilege_id
            ))

        con.execute(privileges_users.insert().values(
            user_id=user_id,
            privilege_id= admin_privilege_id
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

def delete_user_in_subject(db_session, user_id, subject_id):
    db_session.execute('DELETE FROM users_subjects \
    WHERE subject_id = :subject_id AND user_id = :user_id'  , {'subject_id': subject_id, 'user_id': user_id})

    db_session.commit()

    return