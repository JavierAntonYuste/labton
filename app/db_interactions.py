from app import models


def create_user(db_session, engine, name, email):
    user=models.User(first_name=name,email= email)
    db_session.add(user)
    db_session.commit()

    try:
        con = engine.connect()
        trans = con.begin()
        user_id = db_session.query(models.User.id).filter_by(email=email).first()
        role_id = db_session.query(models.Role.id).filter_by(name='user').first()

        # Creating relations
        con.execute(models.roles_users.insert().values(
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
    user=models.User(first_name=name,email= email)
    db_session.add(user)
    db_session.commit()

    try:
        con = engine.connect()
        trans = con.begin()
        user_id = db_session.query(models.User.id).filter_by(email=email).first()
        role_id = db_session.query(models.Role.id).filter_by(name='user').first()
        admin_role_id = db_session.query(models.Role.id).filter_by(name='admin').first()

        # Creating relations
        con.execute(models.roles_users.insert().values(
            user_id=user_id,
            role_id= role_id
            ))

        con.execute(models.roles_users.insert().values(
            user_id=user_id,
            role_id= admin_role_id
            ))

        trans.commit()

    except:
        trans.rollback()
        raise

    con.close()

    return
