# python3.10 -m flask --app model db init
# python2.10 -m flask --app model db merge
# python3.10 -m flask --app model db upgrade
# python3.10 -m flask --app model db migrate
# python3.10 -m flask --app model db upgrade

# imports --------------------------------------------

from flask import g 
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session
from flask_migrate import Migrate
import sqlite3, os
from pathlib import Path
from json import loads, dumps
from pprint import pprint

from main import app


DATBASE_DIR = str(Path(os.path.dirname(__file__)).parent.absolute())
DATABASE_NAME = 'theapp.db'
DATABASE_PATH = DATBASE_DIR + '/' + DATABASE_NAME

with open('./pure_labs.json' , 'r') as f:
    d = f.read()

# init Flask app  --------------------------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ---------------------------------
     
def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key support
    return conn

from contextlib import contextmanager

@contextmanager
def borrowDB():
    connection = get_conn()
    cursor = connection.cursor()
 
    try:
        yield (connection, cursor)
        connection.commit()

    finally:
        connection.close()

@contextmanager
def borrowDbSession():
    with Session(db) as session:
        try:
            yield session
        finally:
            session.commit()


# database structures --------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # a person who is sharing
    subscriber_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # a person who is shared
    project_name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.Text, nullable=True)
    value = db.Column(db.Text, nullable=True)
    
def get_user_value(username, key):
    with borrowDB() as (conn, cursor):
        cursor.execute('''
            SELECT value
            FROM   project
            WHERE 
                username = ? AND
                key      = ?
            ''', (username, key))
        return cursor.fetchone()

def update_user_value(username, key, value):
    with borrowDB() as (conn, cursor):
        cursor.execute('''
            UPDATE project
            SET 
                key = ?,
                value = ?
            FROM user
            WHERE
                user.id = project.owner_user_id AND
                user.username = ? 
            ''', (key, value, username))

def get_user(username):
    with borrowDB() as (conn, cursor):
        cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
        return cursor.fetchone()

def get_user_by_password(username, password):
    with borrowDB() as (conn, cursor):
        cursor.execute('''
                SELECT * 
                FROM user 
                WHERE 
                    username = ? AND 
                    password = ?
                ''', (username, password))

        return  cursor.fetchone()


def create_user(username, password):
    with borrowDbSession() as ss:
        ss.add(User(username=username, password=password,key ="/jade.html",value=d ))
    
def create_project(project_name, owner_user_id):
    with borrowDbSession() as ss:
        ss.add(Project(project_name=project_name, owner_user_id=owner_user_id))


def create_project_with_subscribers(project_name, owner_user_id, subscriber_user_id):
    with borrowDbSession() as ss:
        ss.add(Project(project_name=project_name, owner_user_id=owner_user_id, subscriber_user_id=subscriber_user_id))
def get_user_value_of_shared_project(project_name, username, key):
    with borrowDB() as (conn, cursor):
        cursor.execute('''
            SELECT value
            FROM project
            JOIN usert ON user.id = sharing_project.owner_user_id
            WHERE 
                user.username = ? AND
                user.key = ? AND
                sharing_project.project_name = ? 
            ''', (username, key, project_name))
        return cursor.fetchone()
    
def update_user_value_of_shared_project(value, username, key, project_name):
    with borrowDB() as (conn, cursor):
        cursor.execute('''
            UPDATE project
            SET 
                key = ?,
                value = ?
            FROM user
            WHERE 
                user.id = sharing_project.owner_user_id AND
                user.username = ? AND
                sharing_project.project_name = ?
            ''', (key, value, username, project_name))
    