
# LabTon
Platform developed with the purpose of introducting gamification in laboratories, especifically in electronic laboratories, but it can be extended to any discipline.

It begun as an improvement of the software produce to support an Innovation Project in Education  funded by Universidad Politécnica de Madrid (IE1819.0903), which was applied to students from Bachelor in Biomedical Engineering, having positive outputs.

## Basic structure
In order to provide support the structure of a laboratory, this following structure has been created.

![relations](https://user-images.githubusercontent.com/36293800/73128160-714cf000-3fcb-11ea-994f-9d017ac4bdb8.png)


There are three types of users:

 - **Admins**
		 Person who manages the systems in charge of supporting education, to review their proper functioning and supervision for the proper functioning of these systems.
 - **Professors**
		 Teaching staff dedicated to the creation and management of content for students, implementing the necessary means to support teaching, in this case, managing the activities or milestones (defined below) of the laboratories.
 - **User/Students**
		Object of gamification, which enjoys gamified activities and learning from them in a fun and entertaining way.

There are also identities that are necessary for supporting the labs.

- **Subject**
Discipline taught during an academic year 2 included in a curriculum, with a defined scope.
	- **Grouping**
	A group of students, usually called "class", which serves the organization of students and division of resources, *e.g. Monday or Tuesday groupings.*
	- **Group**
	A subset of grouping, in which few students come together to cooperatively realize a milestone, *e.g. Pair Monday-1, Pair Monday-4.*

- **Practice**
Exercise included in a subject, whose objective is teach certain educational content, following certain rules.
- **Session**
Formalization of the exercise explained above, which can be a practice implemented in several sessions, in different time slots and with different students.
- **Milestone**
Concrete activity, included in a practice and formalized in a session, in which students participate and implement the gamification.


## Installation

This platform has been designed with the idea of making the implementation simple for not taking too much effort in the deployment.

It is compose by 2 Docker ([Docker website](https://www.docker.com/)) containers, one that has the website service ,developed with the framework Flask ([Flask website](https://www.palletsprojects.com/p/flask/)), and the database service, in MySQL ([MySQL website](https://www.mysql.com/)).
### Steps
For recreating the enviroment of this repository, there are some easy steps that should be taken.

 1. Clone the repository in local and enter the folder.

```
git clone git@github.com:greenlsi/labton.git
cd labton/
 ```


 2. Build the containers and then stop them running.
```
docker-compose up --build
```
Then type  Ctrl + C.

3. Run the containers
```
docker-compose up
```
4. Type the direction of locahost ([localhost](localhost)) in your web browser.

#### Remove default admin user
1. Enter with the credentials of the default admin user:

> **Email**: admin
> **Password**: (None)

2. Go to to Users page ([/users](/users)) and add a new user email  with admin privilege(preferably owned by yourself).
3. Logout.
4. Login with the new email account.
5. Go again to Users page ([/users](/users))  and delete default admin user

###  Troubleshooting
If a problem rises with the platform meanwhile it is being used, the problem can be fixed and run again the Docker containers with:
```
docker-compose up
```
## Platform configurations

Some parameters can be configured for the personalised functioning of LabTon, like the IMAP servers for the login.

In order to modify these settings, go to app/appconfig.py.
## Database
The Docker container of the database is, as it is mentioned before, implemented with MySQL. The defined tables schema and their definition can be found in this following figure.

![database](https://user-images.githubusercontent.com/36293800/73128154-54182180-3fcb-11ea-9a19-27061db7dc10.png)

### How to enter database Docker container
If a query or a fix are necessary, for entering the Docker container and in it, the mysql service, you should introduce the following commands.


```
docker exec -it [name of the container] /bin/bash
mysql -u labton -p
	password: labton

----------------------------------------------------------
mysql> use labton
```

For listing all the containers that were created in a machine, you can type:
```
docker ps -a
```
### Migrations

If a change in the database is needed, a migration should be done. For doing so visit  [Migrations folder](app/migrations/) for knowing more details on how to perform it.

## Adding new milestones
This platform has a standardized process for adding new activities that cover the necesities the Education could have.
In order to develop a new kind of milestone, you need:

 1. Add a Python file to app/milestones that contains 2 methods.

	 - Method that verifies the answer provided by the students.
		 ```
		 def verify(data,milestone):
			 return result
		```
	- Method for loading content in the template.
		 ```
		 def load(milestone):
			 return data
		```
	 For more details **check the template** included as app/milestones/template.py.
2. Add a template web file (HTML+CSS+JS).
This file will serve for visualize the page and will enable student to interact with the milestone.

It needs to have a form defined in the following way:
```
<form  action="/verifyMilestone">
	...
	[Enter the input tags here]
	...
	<button type="submit"></button>
</form>
```

 **A template has been included** as app/templates/milestoneViews/template.html.


*Note*: Boostrap source is already added in templates/base.html.

### Support files

For giving support to the milestones, a mechanism for uploading data files has been implemented. Through the platform, specifically in [/practice](/practice) page, a file can be added to the server.

This file can be in any format, recommended in CSV or JSON since they are specifically designed for data transfer.

The instructions for accessing these files are deeply  detailed in /app/milestones/templete.py.
## System requirements

In order to make LabTon run, you will only need Docker, since it is the one responsible of running the services in the containers.

For installing it, [visit this webpage.](https://docs.docker.com/install/)

As this platform is the result of joining two docker images, we should run them using docker-compose as it is stated before. For adding docker-compose, [visit this webpage](https://docs.docker.com/compose/install/).
