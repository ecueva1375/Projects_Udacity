import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# SQLALCHEMY_DATABASE_URI = '<Put your local database url>'
# SQLALCHEMY_DATABASE_URI = 'postgresql:\
#                          //postgres:alexandra1375@localhost:5432/fyyurapp'


class DatabaseURI:
    DATABASE_NAME = "fyyurapp"
    username = 'postgres'
    password = 'alexandra1375'
    url = 'localhost:5432'
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
        username, password, url, DATABASE_NAME)
