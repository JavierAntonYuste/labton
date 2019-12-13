
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

def get_user_by_id(db_session, id):
    user= db_session.query(User).filter(User.id==id).first()
    return user


def get_user(db_session, email ):
    user= db_session.query(User).filter(User.email==email).first()
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

    db_session.execute('DELETE FROM users_group_subject \
    WHERE user_id= :user_id'  , {'user_id': user_id})

    db_session.execute('DELETE FROM users_session\
    WHERE user_id=:user_id'  , {'user_id':user_id})

    db_session.commit()

    # Delete Subject
    db_session.execute('DELETE FROM user \
    WHERE id = :user_id'  , {'user_id': user_id})

    db_session.commit()
    return

# Subject CRUD methods _____________________________________________________________

# INSERT
def create_subject(db_session, acronym, name, degree, year, description):
    subject=Subject(acronym=acronym, name=name, degree= degree, year=year, description=description)
    db_session.add(subject)

    db_session.commit()

    subject_added=db_session.query(Subject).filter(Subject.acronym==acronym, Subject.name==name,\
    Subject.degree==degree, Subject.year==year, Subject.description==description).first()
    return subject_added

# READ

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

def update_subject(db_session, id, acronym, name, degree, year, description):

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
    practices=get_practices(db_session, subject_id)
    for practice in practices:
        delete_practice(db_session,practice.id)

    db_session.execute('DELETE FROM users_subjects \
    WHERE subject_id = :subject_id'  , {'subject_id': subject_id})

    db_session.commit()

    # Delete Subject
    db_session.execute('DELETE FROM subjects \
    WHERE id = :subject_id'  , {'subject_id': subject_id})

    db_session.commit()
    return

# Practice CRUD methods ______________________________________________________________

# INSERT

def create_practice(db_session, name, milestones, rating_way, subject_id, description):
    practice=Practice(name=name, milestones=milestones, rating_way=rating_way, subject_id=subject_id, description=description)
    db_session.add(practice)
    db_session.commit()

    return

# READ

def get_practice(db_session, id):
    practice=db_session.query(Practice).filter(Practice.id==id).first()
    return practice

def get_practices(db_session, subject_id):
    list_practices=db_session.query(Practice).filter(Practice.subject_id==subject_id).all()
    return list_practices

def get_subject_id_practice(db_session, id):
    subject_id=db_session.query(Practice.subject_id).filter_by(id=id).first()
    return subject_id

def get_subject_id_session(db_session, session_id):
    subject_id=db_session.query(Practice.subject_id).\
    join(Session, Practice.id==Session.practice_id).filter(Session.id==session_id).first()
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
    db_session.execute('DELETE FROM milestones \
    WHERE practice_id = :practice_id'  , {'practice_id': id})
    db_session.commit()

    db_session.execute('DELETE FROM practices \
    WHERE id = :id'  , {'id': id})

    db_session.commit()
    return

# Milestones CRUD methods ______________________________________________________________

# INSERT

def create_milestone(db_session, name, mode, practice_id, description):
    milestone=Milestone(name=name, mode=mode, practice_id=practice_id, description=description)
    db_session.add(milestone)
    db_session.commit()

    return

# READ

def get_milestone(db_session, id):
    milestone=db_session.query(Milestone).filter(Milestone.id==id).first()
    return milestone

def get_milestone_id(db_session, name, mode, practice_id):
    milestone=db_session.query(Milestone.id).filter(Milestone.name==name).filter(Milestone.mode==mode).\
    filter(Milestone.practice_id==practice_id).first()

    return milestone

def get_practice_milestones(db_session, practice_id):
    list_milestones=db_session.query(Milestone).filter(Milestone.practice_id==practice_id).all()
    return list_milestones

def get_practice_id_milestone(db_session, id):
    practice_id=db_session.query(Milestone.practice_id).filter_by(id=id).first()
    return practice_id

def get_milestones(db_session):
    milestones=db_session.query(Milestone).all()
    return milestones

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
    return

# Session CRUD methods ______________________________________________________________

# INSERT

def create_session(db_session, name, start_datetime, end_datetime, practice_id, description):
    session=Session(name=name,start_datetime=start_datetime,end_datetime=end_datetime,practice_id=practice_id,description=description)
    db_session.add(session)
    db_session.commit()

    return

# READ

def get_session(db_session, id):
    session=db_session.query(Session).filter(Session.id==id).first()
    return session

def get_session_from_param(db_session,name, start_datetime, end_datetime, practice_id, description):
    session=db_session.query(Session).filter(Session.name==name, Session.start_datetime==start_datetime, Session.end_datetime==end_datetime,\
    Session.practice_id==practice_id, Session.description==description).first()
    return session

def get_sessions_from_practice(db_session, practice_id):
    sessions=db_session.query(Session).filter(Session.practice_id==practice_id).all()
    return sessions

def get_sessions_from_subject(db_session, subject_id):
    sessions=db_session.query(Session).\
    join(Practice, Session.practice_id==Practice.id).\
    filter(Practice.subject_id==subject_id).all()
    return sessions

# def get_session_id(db_session, name, mode, practice_id):
#     return milestone

# UPDATE

def update_session(db_session,id, name, start_datetime, end_datetime, practice_id, description):
    db_session.execute('UPDATE sessions\
    SET name = :name, start_datetime=:start_datetime,end_datetime=:end_datetime, practice_id=:practice_id, description=:description WHERE id = :id',\
    {'name': name,\
     'start_datetime': start_datetime, \
     'end_datetime': end_datetime,\
     'practice_id': practice_id,\
     'description': description,\
     'id': id})

    db_session.commit()
    return

# DELETE


def delete_session(db_session, id):
    db_session.execute('DELETE FROM users_session\
    WHERE session_id= :session_id' , {'session_id': id})

    db_session.commit()

    db_session.execute('DELETE FROM sessions \
    WHERE id = :id'  , {'id': id})

    db_session.commit()
    return


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

    db_session.execute('DELETE FROM users_group_subject \
    WHERE user_id= :user_id'  , {'user_id': user_id})

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

# groupings_subject CRUD methods__________________________________________________

# INSERT

def add_grouping_subject_session(db_session, name, subject_id):
    db_session.execute('INSERT INTO groupings_subject(name, subject_id) \
    VALUES (:name,:subject_id)'  , {'name': name, 'subject_id': subject_id})

    db_session.commit()

    return

# READ
def get_grouping(db_session, grouping_id):
    grouping=db_session.query(groupings_subject).filter(groupings_subject.c.grouping_id==grouping_id).first()
    return grouping

def get_grouping_by_name_and_subject(db_session, name, subject_id):
    grouping=db_session.query(groupings_subject).\
    filter(groupings_subject.c.name==name).filter(groupings_subject.c.subject_id==subject_id).first()
    return grouping

def get_groupings_in_subject(db_session, subject_id):
    groupings= db_session.query(groupings_subject).filter(groupings_subject.c.subject_id==subject_id).all()
    return groupings


# UPDATE

def update_grouping(db_session,grouping_id, name, subject_id):

    db_session.execute('UPDATE groupings_subject\
    SET name = :name AND subject_id = :subject_id WHERE grouping_id = :grouping_id',\
    {'name': name,\
     'subject_id': subject_id, \
     'grouping_id': grouping_id })

    db_session.commit()
    return

# DELETE
def delete_grouping_subject(db_session, grouping_id):
    db_session.execute('DELETE users_group_subject FROM users_group_subject \
    INNER JOIN groups_subject ON users_group_subject.group_id = groups_subject.group_id \
    WHERE groups_subject.grouping_id = :grouping_id;',{'grouping_id':grouping_id})
    db_session.commit()


    db_session.execute('DELETE groups_subject FROM groups_subject \
    JOIN groupings_subject on groups_subject.grouping_id=groupings_subject.grouping_id\
    WHERE groupings_subject.grouping_id = :grouping_id;',\
    {'grouping_id': grouping_id})
    db_session.commit()


    db_session.execute('DELETE FROM groupings_subject \
    WHERE grouping_id = :grouping_id'  , {'grouping_id': grouping_id})
    db_session.commit()

    return

# groups_subject CRUD methods__________________________________________________

# INSERT

def add_group_subject_session(db_session, name, grouping_id):
    db_session.execute('INSERT INTO groups_subject(name, grouping_id) \
    VALUES (:name,:grouping_id)'  , {'name': name, 'grouping_id': grouping_id})

    db_session.commit()

    return

# READ
def get_group(db_session, group_id):
    group=db_session.query(groups_subject).filter(groups_subject.c.group_id==group_id).first()
    return group

def get_groups_in_subject(db_session, subject_id):
    groups=db_session.query(groups_subject).\
    join(groupings_subject, groups_subject.c.grouping_id==groupings_subject.c.grouping_id).\
    filter(groupings_subject.c.subject_id==subject_id).all()

    return groups

def get_group_by_name_and_subject(db_session, name, subject_id):
    group=db_session.query(groups_subject).\
    join(groupings_subject, groups_subject.c.grouping_id==groupings_subject.c.grouping_id).\
    filter(groups_subject.c.name==name).filter(groupings_subject.c.subject_id==subject_id).first()
    return group

def get_groups_grouping(db_session, grouping_id):
    groups= db_session.query(groups_subject).filter(groups_subject.c.grouping_id==grouping_id).all()
    return groups


def get_group_from_user_in_subject(db_session, user_id, subject_id):
    group=db_session.query(groups_subject).\
    join(users_group_subject,groups_subject.c.group_id==users_group_subject.c.group_id).\
    join(groupings_subject, groups_subject.c.grouping_id==groupings_subject.c.grouping_id).\
    filter(users_group_subject.c.user_id==user_id).\
    filter(groupings_subject.c.subject_id==subject_id).first()

    return group

def get_group_session(db_session, user_id, practice_id):
    group=db_session.query(groups_subject).\
    join(users_group_subject,groups_subject.c.group_id==users_group_subject.c.group_id).\
    join(groupings_subject, groups_subject.c.grouping_id==groupings_subject.c.grouping_id).\
    join(Subject, groupings_subject.c.subject_id==Subject.id).\
    join(Practice, Subject.id==Practice.subject_id).\
    filter(Practice.id==practice_id).filter(users_group_subject.c.user_id==user_id).first()

    return group

# UPDATE

def update_group(db_session,group_id, name, grouping_id):

    db_session.execute('UPDATE groups_subject\
    SET name = :name AND grouping_id = :grouping_id WHERE group_id = :group_id',\
    {'name': name,\
     'grouping_id': groupings_id, \
     'group_id': group_id })

    db_session.commit()
    return

# DELETE
def delete_group_subject(db_session,group_id):
    db_session.execute('DELETE FROM users_group_subject \
    JOIN groups_subject ON users_group_subject.group_id=groups_subject.group_id\
    WHERE groups_subject.group_id = :group_id',\
    {'group_id': group_id})


    db_session.execute('DELETE FROM groups_subject \
    WHERE group_id = :group_id'  , {'group_id': group_id})

    db_session.commit()

    return

# users_group_subject CRUD methods__________________________________________________

# INSERT

def add_user_group_subject(engine, group_id, user_id):
    con = engine.connect()
    trans = con.begin()
    try:

        # Creating relations
        con.execute(users_group_subject.insert().values(
            group_id=group_id,
            user_id=user_id
            ))

        trans.commit()

    except:
        trans.rollback()
        raise

    con.close()
    return

# READ

def get_user_ids_group(db_session, group_id):
    users_id= db_session.query(users_group_subject).filter(users_group_subject.c.group_id==group_id).all()
    return users_id

def get_group_id_user(db_session, user_id):
    groups= db_session.query(users_group_subject.c.group_id).filter(users_group_subject.c.user_id==user_id).all()
    return groups

def get_users_in_grouping(db_session, grouping_id):
    users=db_session.query(users_group_subject).\
    join(groups_subject, users_group_subject.c.group_id==groups_subject.c.group_id).\
    join(groupings_subject, groups_subject.c.grouping_id==groupings_subject.c.grouping_id).\
    filter(groupings_subject.c.grouping_id==grouping_id).all()
    return users


# UPDATE

def update_user_group(db_session,old_group_id, group_id, user_id):
    db_session.execute('UPDATE users_group_subject\
    SET group_id = :group_id WHERE user_id = :user_id AND group_id = :old_group_id',\
    {'group_id': group_id, \
    'user_id': user_id,
    'old_group_id':old_group_id})

    db_session.commit()

    return

# DELETE
def delete_user_group_subject(db_session,user_id, group_id):

    db_session.execute("DELETE FROM users_group_subject \
    WHERE group_id = :group_id AND user_id = :user_id", \

    {'group_id': group_id,\
    'user_id': user_id})

    db_session.commit()

    return


# groups_subject CRUD methods__________________________________________________

# INSERT

def add_group_subject_session(db_session, name, grouping_id):
    db_session.execute('INSERT INTO groups_subject(name, grouping_id) \
    VALUES (:name,:grouping_id)'  , {'name': name, 'grouping_id': grouping_id})

    db_session.commit()

    return

# READ
def get_group(db_session, group_id):
    group=db_session.query(groups_subject).filter(groups_subject.c.group_id==group_id).first()
    return group

def get_groups_in_subject(db_session, subject_id):
    groups=db_session.query(groups_subject).\
    join(groupings_subject, groups_subject.c.grouping_id==groupings_subject.c.grouping_id).\
    filter(groupings_subject.c.subject_id==subject_id).all()

    return groups

def get_group_by_name_and_subject(db_session, name, subject_id):
    group=db_session.query(groups_subject).\
    join(groupings_subject, groups_subject.c.grouping_id==groupings_subject.c.grouping_id).\
    filter(groups_subject.c.name==name).filter(groupings_subject.c.subject_id==subject_id).first()
    return group

def get_groups_grouping(db_session, grouping_id):
    groups= db_session.query(groups_subject).filter(groups_subject.c.grouping_id==grouping_id).all()
    return groups


def get_group_from_user_in_subject(db_session, user_id, subject_id):
    group=db_session.query(groups_subject).\
    join(users_group_subject,groups_subject.c.group_id==users_group_subject.c.group_id).\
    join(groupings_subject, groups_subject.c.grouping_id==groupings_subject.c.grouping_id).\
    filter(users_group_subject.c.user_id==user_id).\
    filter(groupings_subject.c.subject_id==subject_id).first()

    return group

# UPDATE

def update_group(db_session,group_id, name, grouping_id):

    db_session.execute('UPDATE groups_subject\
    SET name = :name AND grouping_id = :grouping_id WHERE group_id = :group_id',\
    {'name': name,\
     'grouping_id': groupings_id, \
     'group_id': group_id })

    db_session.commit()
    return

# DELETE
def delete_group_subject(db_session,group_id):
    db_session.execute('DELETE FROM groups_subject \
    WHERE group_id = :group_id'  , {'group_id': group_id})

    db_session.commit()

    return

# users_group_subject CRUD methods__________________________________________________

# INSERT

def add_milestone_dependency(db_session, milestone_id, depending_milestone_id):
    db_session.execute('INSERT INTO milestone_dependencies(milestone_id, dependency_id) \
    VALUES (:milestone_id,:depending_milestone_id)'  , {'milestone_id': milestone_id, 'depending_milestone_id': depending_milestone_id})

    db_session.commit()
    return


# READ

def get_milestone_dependencies(db_session, milestone_id):
    dependencies=db_session.query(milestone_dependencies).filter(milestone_dependencies.c.milestone_id==milestone_id).all()
    return dependencies


# UPDATE


# DELETE

def delete_dependencies(db_session, milestone_id):
    db_session.execute('DELETE FROM milestone_dependencies\
    WHERE milestone_id = :milestone_id'  , {'milestone_id': milestone_id})

    db_session.commit()

    return

def delete_dependency(db_session, milestone_id, dependency_id):
    db_session.execute('DELETE FROM milestone_dependencies\
    WHERE milestone_id = :milestone_id AND dependency_id = :dependency_id'  , {'milestone_id': milestone_id, 'dependency_id': dependency_id})

    db_session.commit()
    return

# users_session CRUD methods__________________________________________________

# INSERT

def add_user_session(db_session, session_id,user_id,group_id,points):
    db_session.execute('INSERT INTO users_session(session_id,user_id,group_id,points) \
    VALUES (:session_id,:user_id,:group_id,:points)'  , \
    {'session_id': session_id, \
    'user_id': user_id,\
    'group_id': group_id,
    'points': points
    })

    db_session.commit()
    return


# READ
def get_session(db_session, session_id):
    session=db_session.query(Session).filter(Session.id==session_id).first()
    return session

def get_user_session(db_session, session_id, user_id):
    user_session=db_session.query(users_session).filter(users_session.c.session_id==session_id)\
    .filter(users_session.c.user_id==user_id).first()
    return user_session

def get_users_in_session(db_session,session_id):
    users=db_session.query(users_session.c.user_id, users_session.c.group_id).filter(users_session.c.session_id==session_id).all()
    return users

def get_sessions_from_user(db_session, user_id):
    user_sessions=db_session.query(users_session).filter(users_session.c.user_id==user_id).all()
    return user_sessions

def get_points_session(db_session, session_id, user_id):
    points=db_session.query(users_session.c.points).filter(users_session.c.session_id==session_id).filter(users_session.c.user_id==user_id).first()
    return points

def get_top_3_points(db_session, session_id):
    top=db_session.execute('SELECT user_id, points FROM users_session WHERE session_id = :session_id ORDER BY points DESC LIMIT 3',\
    {'session_id': session_id
    }).fetchall()

    return top

def get_groups_points_session(db_session, session_id):
    # groups=db_session.query(users_session).distinct(users_session.c.group_id).order_by(desc(users_session.c.points)).\
    # filter(users_session.c.session_id==session_id).all()

    groups=db_session.execute('SELECT DISTINCT group_id, points FROM users_session \
    WHERE session_id=:session_id\
    ORDER BY points DESC',{'session_id': session_id}).fetchall()

    return groups

# UPDATE

def update_user_session_points(db_session,session_id,user_id,points):
    db_session.execute('UPDATE users_session\
    SET points= :points WHERE session_id=:session_id AND user_id = :user_id',\
    {'points': points,
    'session_id': session_id,
    'user_id': user_id
    })

    db_session.commit()
    return

# DELETE

def delete_user_in_session(db_session, session_id, user_id):
    db_session.execute('DELETE FROM users_session\
    WHERE session_id= :session_id AND user_id=:user_id'  , {'session_id': session_id, 'user_id':user_id})

    db_session.commit()

    return
