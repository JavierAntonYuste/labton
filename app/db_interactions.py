from app.models import *

# INSERT queries __________________________________________________________________-
def create_user(db_session, engine, name, email, privilege_name):
    user=User(username=name,email= email)
    db_session.add(user)
    db_session.commit()

    try:
        con = engine.connect()
        trans = con.begin()
        user_id = db_session.query(User.id).filter_by(email=email).first()
        privilege_id = db_session.query(Privilege.id).filter_by(name=privilege_name).first()

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

def create_subject(db_session, acronym, name, degree, year, description):
    # subject=Subjects(acronym="hola", name=name, year=2019, degree='GITST', description="")
    # db_session.add(subject)
    db_session.execute('INSERT INTO subjects(acronym,name,year,degree,description) VALUES (:acronym,:name,:year,:degree,:description)',\
    {'acronym': acronym, 'name':name, 'year':year, 'degree':degree, 'description':description})

    db_session.commit()
    return

def add_user_to_subject(db_session, engine, email, subject_id, role_name ):
        try:
            con = engine.connect()
            trans = con.begin()
            user_id = db_session.query(User.id).filter_by(email=email).first()
            role_id = db_session.query(Role.id).filter_by(name=role_name).first()

            # Creating relations
            con.execute(users_subjects.insert().values(
                user_id=user_id,
                role_id=role_id,
                subject_id=subject_id
                ))

            trans.commit()

        except:
            trans.rollback()
            raise

        con.close()

        return

# SELECT queries _______________________________________________________________

def get_users(db_session):
    users= db_session.query(privileges_users.c.user_id,privileges_users.c.privilege_id).all()
    return users

def get_role_subject(db_session, email, id):
    role=(db_session.query(Role.name).\
    join(users_subjects, Role.id==users_subjects.c.role_id).join(User, users_subjects.c.user_id==User.id).\
    filter(User.email==email).filter(users_subjects.c.subject_id==id).first())[0]

    return role

def get_users_in_subject (db_session, subject_id ):
    users=db_session.query(users_subjects.c.user_id, users_subjects.c.role_id)\
    .filter(users_subjects.c.subject_id==subject_id).all()

    return users

def get_privileges(db_session, email):
    privileges=db_session.query(Privilege)\
    .join(privileges_users, Privilege.id==privileges_users.c.privilege_id)\
    .join(User, privileges_users.c.user_id==User.id)\
    .filter(User.email==email).all()

    return privileges

def get_user_id(db_session, email):
    user_id= db_session.query(User.id).filter_by(email=email).first()
    return user_id


# DELETE queries ___________________________________________________________________
def delete_user_in_subject(db_session, user_id, subject_id):
    db_session.execute('DELETE FROM users_subjects \
    WHERE subject_id = :subject_id AND user_id = :user_id'  , {'subject_id': subject_id, 'user_id': user_id})

    db_session.commit()

    return

def delete_subject(db_session, subject_id):
    # Delete relations
    db_session.execute('DELETE FROM users_subjects \
    WHERE subject_id = :subject_id'  , {'subject_id': subject_id})
    db_session.commit()

    # Delete Subject
    db_session.execute('DELETE FROM subjects \
    WHERE id = :subject_id'  , {'subject_id': subject_id})

    db_session.commit()

def delete_user(db_session, user_id):
    # Delete relations
    db_session.execute('DELETE FROM users_subjects \
    WHERE user_id= :user_id'  , {'user_id': user_id})

    db_session.execute('DELETE FROM privileges_users \
    WHERE user_id= :user_id'  , {'user_id': user_id})

    db_session.commit()

    # Delete Subject
    db_session.execute('DELETE FROM user \
    WHERE id = :user_id'  , {'user_id': user_id})

    db_session.commit()
