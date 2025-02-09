# python3.10 -m flask --app model db init
# python2.10 -m flask --app model db merge
# python3.10 -m flask --app model db upgrade
# python3.10 -m flask --app model db migrate
# python3.10 -m flask --app model db upgrade

# imports --------------------------------------------
from flask import request
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
    otp_code =  db.Column(db.Integer)
    
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100),nullable = False)
    owner_user_id = db.Column(db.ForeignKey('user.id'),nullable = True)
    value = db.Column(db.Text, nullable=True)
    
    owner = db.relationship('User', foreign_keys=[owner_user_id], backref='owned_projects')
    
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.ForeignKey('project.id'),nullable = False)
    subscriber_user_id = db.Column(db.ForeignKey('user.id'),nullable = True) 
    
    subscriber = db.relationship('User', foreign_keys=[subscriber_user_id], backref='shared_projects')
    proj_id= db.relationship('Project', foreign_keys=[project_id], backref='proj_id')
    
def get_user(username):
    return User.query.filter(User.username == username).first()

def get_user_by_ids(selected_user_ids):
    users = User.query.filter(User.id.in_(selected_user_ids)).all()
    return  users

def create_user(username, password,email,otp_code):
    with borrowDbSession() as ss:
        ss.add(User(username=username, password=password, email=email,otp_code=otp_code))
        
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
        owner_user_id      = owner_id).first()
   
def get_project_by_project_id(p_id):
    return Project.query.get(p_id)
    
def create_empty_project(project_name, owner_user_id):
    with borrowDbSession() as ss:
        p = Project(
            project_name=project_name, 
            owner_user_id=owner_user_id,
            value = '{}')
        ss.add(p)
        ss.flush() # save to get id
        return p.id

def create_empty_project(project_name, owner_user_id):
    with borrowDbSession() as ss:
        p = Project(
            project_name=project_name, 
            owner_user_id=owner_user_id, 
            value = '{}')
        ss.add(p)
        ss.flush() 
        return p.id
    
def subscribe_to_proj(proj, users):
    with borrowDbSession() as ss:
        for subscriber in users:
            new_subscription = Subscription(
                project_id         = proj.id,
                subscriber_user_id = subscriber.id
            )
        ss.add(new_subscription)
        ss.flush()
        ss.commit()
        
