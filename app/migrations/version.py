"""empty message

Revision ID: revisionID
Revises:
Create Date: revisionDate

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'revisionID'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
  # Dropping relation tables
  op.drop_table('privileges_users')
  op.drop_table('users_subjects')
  op.drop_table('users_group_subject')
  op.drop_table('groups_subject')
  op.drop_table('groupings_subject')
  op.drop_table('users_session')
  op.drop_table('milestone_dependencies')
  op.drop_table('milestone_log')

  #Droping models dependant on others

  op.drop_table('sessions')
  op.drop_table('milestones')
  op.drop_table('practices')

  # Dropping the rest of tables
  op.drop_table('role')
  op.drop_table('privilege')
  op.drop_table('user')
  op.drop_table('subjects')

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users_subjects',
    sa.Column('subject_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('role_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name='users_subjects_ibfk_3'),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name='users_subjects_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='users_subjects_ibfk_2'),
    sa.PrimaryKeyConstraint('subject_id', 'user_id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('privileges_users',
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('privilege_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['privilege_id'], ['privilege.id'], name='privileges_users_ibfk_2'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='privileges_users_ibfk_1'),
    sa.PrimaryKeyConstraint('user_id', 'privilege_id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('subjects',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('acronym', mysql.VARCHAR(length=10), nullable=False),
    sa.Column('name', mysql.VARCHAR(length=100), nullable=False),
    sa.Column('year', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('description', mysql.VARCHAR(length=1000), nullable=True),
    sa.Column('degree', mysql.VARCHAR(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('practices',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('milestones', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('rating_way', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('subject_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], name='practices_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_table('user',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.Column('username', mysql.VARCHAR(length=255), nullable=False),
    sa.Column('email', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_index('email', 'user', ['email'], unique=True)
    op.create_table('privilege',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_index('name', 'privilege', ['name'], unique=True)
    op.create_table('role',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_index('name', 'privilege', ['name'], unique=True)
    op.create_table('role',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(length=80), nullable=False),
    sa.Column('description', mysql.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='latin1',
    mysql_engine='InnoDB'
    )
    op.create_index('name', 'role', ['name'], unique=True)
    # ### end Alembic commands ###
