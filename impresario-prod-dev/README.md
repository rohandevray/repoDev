# Installation and Setup
## Prerequisites
- [Python 3.x](https://www.python.org/downloads/)
- [Pip](https://pip.pypa.io/en/stable/installation/)
- [PostgreSQL](https://www.postgresql.org/download/)

## Instructions
- Clone the repo to you local system ```git clone <URL>```
- Create a virtual environment ```python3 -m venv <Name of your choice>```
- Activate the environment ```source <Name of your environment you gave in previous step>/bin/activate```
- Switch to the branch ```dev``` using ```git checkout -b dev```
- Create a new database in PostgreSQL using Pgadmin/shell.
- Go to ``impresario/settings.py`` and under database change the database name, username and passowrd you gave while setting up PostgreSQL
- On you terminal run ```pip install -r requirements.txt```. This will install all the required packages.
- For migrating the changes into your database run ```python3 manage.py migrate```
- Now to run the server locally, ```python3 manage.py runserver``` and check on [localhost::8000](https://localhost:8000)

# For Mentees in NITK Winter of code.
- Create a branch from ```dev``` with ```<frontend/backend>-<your name>```. The command is  ```git checkout -b <name of your branch> dev```.
- Make your changes in this branch and push them.
- Create a PR to merge it with dev and request a review to all the mentors.
