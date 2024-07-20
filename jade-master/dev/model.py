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

# with open('./pure_labs.json' , 'r') as f:
#     d = f.read()
d= '{}'
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
    email = db.Column(db.String(100), nullable=False)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # a person who is sharing
    subscriber_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # a person who is shared
    project_name = db.Column(db.String(100), nullable=False)
    key = db.Column(db.Text, nullable=True)
    value = db.Column(db.Text, nullable=True)
    isAccepted = db.Column(db.Boolean, nullable=True )

    owner = db.relationship('User', foreign_keys=[owner_user_id], backref='owned_projects')
    subscriber = db.relationship('User', foreign_keys=[subscriber_user_id], backref='shared_projects')
    


def get_user(username):
    return User.query.filter(User.username == username).first()


def get_user_by_ids(selected_user_ids):
    users = User.query.filter(User.id.in_(selected_user_ids)).all()
    return  users


def create_user(username, password,email):
    with borrowDbSession() as ss:
        ss.add(User(username=username, password=password, email=email))
        
def get_user_by_password(username, password):
    return User.query.filter(
        User.username == username,
        User.password == password,
        ).first()

def all_users():
    return User.query.all()   

def update_value_of_project(project_id , value ):
    with borrowDB() as (conn, cursor):
        cursor.execute('''
            UPDATE project
            SET
                value = ?
            WHERE
                id = ?
            ''', (value, project_id))
        
def get_all_projects():
    return Project.query.all()
         
def get_project(proj_name, owner_id):
    return Project.query.filter_by(
        project_name       = proj_name, 
        owner_user_id      = owner_id,
        subscriber_user_id = owner_id,
        isAccepted         =  None ).first()
   
def get_project_by_project_id(p_id):
    return Project.query.get(p_id)
    
def create_empty_project(project_name, owner_user_id):
    with borrowDbSession() as ss:
        p = Project(
            project_name=project_name, 
            owner_user_id=owner_user_id, 
            subscriber_user_id = owner_user_id,
            value = '{}' ,
            isAccepted = None)
        ss.add(p)
        ss.flush() # save to get id
        return p.id
    
def subscribe_to_proj(proj, users):
    with borrowDbSession() as ss:
        for subscriber in users:
            new_subscription = Project(
                owner_user_id      = proj.owner_user_id,
                project_name       = proj.project_name,
                subscriber_user_id = subscriber.id, 
                isAccepted         = False
            )
            ss.add(new_subscription)
        ss.commit()

def is_requsted(proj):
    with borrowDbSession() as ss:
        if proj.is_Accepted == False:
            return True
        
        
def set_accept(proj):
    project_id = proj.id
    with borrowDB() as (conn, cursor):
        cursor.execute('''
            UPDATE project
            SET
                is_Accepted = ?
            WHERE
                id = ?
            ''', (1, project_id))