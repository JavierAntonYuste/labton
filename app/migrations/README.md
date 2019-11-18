# How to migrate Database

This project is using [SQLAlchemy](https://www.sqlalchemy.org/), specifically [Alembic](https://alembic.sqlalchemy.org/en/latest/) for migrating the database through the [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) package. So, if you want to change the schema of the database for any reason, you should do the migrations manually.

### Why?

 Alembic generates the migrations upgrade automatically and the order of the process of dropping the database schema is totally random.

The database of this project includes relations between the tables, and this issue with alembic makes the automatic migration hardly ever possible.

### Process

In order to perform the migration of the database you should enter the docker container with the following command.

    docker ps
    docker exec -it <name of your website container> /bin/bash
    
Once inside, you could start with the migrations, starting with this command:

    flask db init

This will create a directory called migrations in your /home/App directory which contains some configuration files for the initial migration, but it should be edited.

Before you perform the upgrade, you should write this commands in the shell:

    cd /home/App/migrations/versions
    nano <Your current alembic version>.py
    
And once inside the document, you must overwrite the order of the method upgrade as following.

~~~
def upgrade():
  # Dropping dependant tables
  op.drop_table('privileges_users')
  op.drop_table('users_subjects')
  op.drop_table('practices')
  
  # Dropping the rest of tables
  op.drop_table('role')
  op.drop_table('privilege')
  op.drop_table('user')
  op.drop_table('subjects')
~~~

After doing this, you can do now the migration upgrade with the command

    flask db migrate
    
### Example
    
There is an example in this folder of a version.py file if you would like to see how is the script of the migrations. More info can be found in the documentation of [SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/en/latest/) and [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/), specially in this last one.