
from app.models import *


# User CRUD methods___________________________________________________

# INSERT
def create_user(db_session, engine, name, email, privilege_name):
    user=User(username=name,email= email)
    db_session.add(user)
    db_session.commit()

    add_privilege_to_user(db_session, engine, email, privilege_name)

    return

# READ
def get_user_id(db_session, email):
    id= db_session.query(User.id).filter(User.email==email).first()
    return id
    def get_user_id(db_session, email):
        user_id= db_session.query(User.id).filter_by(email=email).first()
        return user_id

def get_user_by_id(db_session, id):
    user= db_session.query(User).filter(User.id==id).one()
    return user


def get_user(db_session, email ):
    user= db_session.query(User).filter(User.email==email).one()
    return user

# UPDATE
def update_user(db_session, email, username):
    db_session.execute('UPDATE user\
    SET username = :username WHERE email = :email',\
    {'username': username,\
     'email': email})

    db_session.commit()
    return

# DELETE

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

# Subject CRUD methods _____________________________________________________________

# INSERT
def create_subject(db_session, acronym, name, degree, year, description):
    subject=Subject(acronym=acronym, name=name, degree= degree, year=year, description=description)
    db_session.add(subject)
    # db_session.execute('INSERT INTO subjects(acronym,name,year,degree,description) VALUES (:acronym,:name,:year,:degree,:description)',\
    # {'acronym': acronym, 'name':name, 'year':year, 'degree':degree, 'description':description})

    db_session.commit()
    return

# READ

def get_subject_id(db_session, acronym,year, degree):
    id=db_session.query(Subject.id).filter(Subject.acronym==acronym).filter(Subject.degree==degree).filter(Subject.year==year).first()
    return id

def get_subject(db_session,id):
    subject= db_session.query(Subject).filter(Subject.id==id).one()
    return subject

def get_all_subjects(db_session):
    subjects=db_session.query(Subject).all()
    return subjects

def get_subject_by_year(db_session, id, year):
    subject= db_session.query(Subject).filter_by(id=id,year=year).all()
    return subject

# UPDATE

def update_subject(db_session, id, acronym, name, year, description, degree):

    db_session.execute('UPDATE subjects\
    SET acronym = :acronym, name=:name, year=:year, description=:description, degree=:degree WHERE id = :id',\
    {'acronym': acronym,\
     'name': name, \
     'year': year, \
     'description': description,\
     'degree': degree,
     'id': id})

    db_session.commit()
    return

# DELETE

def delete_subject(db_session, subject_id):
    # Delete relations
    db_session.execute('DELETE FROM users_subjects \
    WHERE subject_id = :subject_id'  , {'subject_id': subject_id})
    db_session.commit()

    # Delete Subject
    db_session.execute('DELETE FROM subjects \
    WHERE id = :subject_id'  , {'subject_id': subject_id})

    db_session.commit()

# Practice CRUD methods ______________________________________________________________

# INSERT

def create_practice(db_session, name, milestones, rating_way, subject_id, description):
    practice=Practice(name=name, milestones=milestones, rating_way=rating_way, subject_id=subject_id, description=description)
    db_session.add(practice)
    db_session.commit()

    return

# READ

def get_practice_id(db_session, name, subject_id):
    id=db_session.query(Practice.id).filter(Practice.name==name).filter(Practice.subject_id==subject_id).first()
    return id

def get_practice(db_session, id):
    practice=db_session.query(Practice).filter(Practice.id==id).first()
    return practice

def get_practices(db_session, subject_id):
    list_practices=db_session.query(Practice).filter(Practice.subject_id==subject_id).all()
    print (list_practices)
    return list_practices

def get_subject_id_practice(db_session, id):
    subject_id=db_session.query(Practice.subject_id).filter_by(id=id).first()
    return subject_id

# UPDATE

def update_practice(db_session,id, name, milestones, rating_way, subject_id, description):
    db_session.execute('UPDATE practices\
    SET name = :name, milestones=:milestones, rating_way=:rating_way, subject_id=:subject_id, description=:description WHERE id = :id',\
    {'name': name,\
     'milestones': milestones, \
     'rating_way': rating_way, \
     'subject_id': subject_id,\
     'description': description,
     'id': id})

    db_session.commit()
    return

# DELETE


def delete_practice(db_session, id):
    db_session.execute('DELETE FROM practices \
    WHERE id = :id'  , {'id': id})

    db_session.commit()

# Milestones CRUD methods ______________________________________________________________

# INSERT

def create_milestone(db_session, name, mode, practice_id, description):
    milestone=Milestone(name=name, mode=mode, practice_id=practice_id, description=description)
    db_session.add(milestone)
    db_session.commit()

    return

# READ

def get_milestone_id(db_session, name, practice_id):
    id=db_session.query(Milestone.id).filter(Milestone.name==name).filter(Milestone.practice_id==practice_id).first()
    return id

def get_milestone(db_session, id):
    milestone=db_session.query(Milestone).filter(Milestone.id==id).first()
    return milestone

def get_practices_milestones(db_session, practice_id):
    list_milestones=db_session.query(Milestone).filter(Milestone.practice_id==practice_id).all()
    return list_milestones

def get_practice_id_milestone(db_session, id):
    practice_id=db_session.query(Milestone.practice_id).filter_by(id=id).first()
    return practices_id

# UPDATE

def update_milestone(db_session,id, name, mode, practice_id, description):
    db_session.execute('UPDATE milestones\
    SET name = :name, mode=:mode, practice_id=:practice_id, description=:description WHERE id = :id',\
    {'name': name,\
     'mode': mode, \
     'practice_id': practice_id,\
     'description': description,
     'id': id})

    db_session.commit()
    return

# DELETE


def delete_milestone(db_session, id):
    db_session.execute('DELETE FROM milestone \
    WHERE id = :id'  , {'id': id})

    db_session.commit()


# Role CRUD methods _____________________________________________________________

# READ
def get_roles(db_session):
    roles=db_session.query(Role).all()
    return roles

def get_role(db_session, id):
    role=db_session.query(Role).filter(Role.id==id).one()
    return role

# Privilege CRUD methods _____________________________________________________________

# READ
def get_privileges(db_session):
    privileges=db_session.query(Privilege).all()
    return privileges

def get_privilege(db_session, id):
    privilege=db_session.query(Privilege).filter(Privilege.id==id).one()
    return privilege

# Relational Tables_________________________________________________________________

# users_subjects CRUD methods__________________________________________________

# INSERT

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

# READ

def get_users_in_subject (db_session, subject_id ):
    users=db_session.query(users_subjects.c.user_id, users_subjects.c.role_id)\
    .filter(users_subjects.c.subject_id==subject_id).all()

    return users

def get_subjects_from_user(db_session, user_id):
    subjects_id= db_session.query(users_subjects.c.subject_id).filter(users_subjects.c.user_id==user_id).all()
    return subjects_id

def get_role_subject(db_session, email, id):
    role=(db_session.query(Role.name).\
    join(users_subjects, Role.id==users_subjects.c.role_id).join(User, users_subjects.c.user_id==User.id).\
    filter(User.email==email).filter(users_subjects.c.subject_id==id).first())[0]

    return role

def check_user_in_subject(db_session, subject_id, user_id):
    query=db_session.query(users_subjects).filter_by(subject_id=subject_id)\
    .filter_by(user_id=user_id).first()

    if query==None:
        return False
    return True

# UPDATE

def update_role(db_session, email, role, subject_id):
    user_id= db_session.query(User.id).filter(User.email==email).first()
    role_id= db_session.query(Role.id).filter(Role.name==role).first()

    db_session.execute('UPDATE users_subjects\
    SET role_id = :role_id WHERE user_id = :user_id AND subject_id= :subject_id',\
    {'role_id': role_id,\
     'user_id': user_id, \
     'subject_id':  subject_id})

    db_session.commit()
    return

# DELETE

def delete_user_in_subject(db_session, user_id, subject_id):
    db_session.execute('DELETE FROM users_subjects \
    WHERE subject_id = :subject_id AND user_id = :user_id'  , {'subject_id': subject_id, 'user_id': user_id})

    db_session.commit()

    return

# privileges_users CRUD methods__________________________________________________

# INSERT

def add_privilege_to_user(db_session, engine, email,privilege_name):

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

# READ

def get_users_privileges(db_session):
    users= db_session.query(privileges_users.c.user_id,privileges_users.c.privilege_id).all()
    return users

def get_user_privileges(db_session, email):
    privileges=db_session.query(Privilege)\
    .join(privileges_users, Privilege.id==privileges_users.c.privilege_id)\
    .join(User, privileges_users.c.user_id==User.id)\
    .filter(User.email==email).first()

    return privileges

# UPDATE

def update_privilege(db_session, email, privilege):
    user_id= db_session.query(User.id).filter(User.email==email).first()
    privilege_id= db_session.query(Privilege.id).filter(Privilege.name==privilege).first()

    db_session.execute('UPDATE privileges_users\
    SET privilege_id = :privilege_id WHERE user_id = :user_id',\
    {'privilege_id': privilege_id,\
     'user_id': user_id, \
     })

    db_session.commit()
    return

# DELETE
# Not exists, it doesn't make sense to have a user without privilege relations
