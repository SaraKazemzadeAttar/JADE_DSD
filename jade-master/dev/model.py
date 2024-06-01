# python3.10 -m flask --app model db init
# python2.10 -m flask --app model db merge
# python3.10 -m flask --app model db upgrade
# python3.10 -m flask --app model db migrate
# python3.10 -m flask --app model db upgrade

# imports --------------------------------------------

from flask import Flask, request, send_from_directory, jsonify, make_response, redirect, url_for, render_template, abort , g 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3, os
from pathlib import Path

from main import app


DATBASE_DIR = str(Path(os.path.dirname(__file__)).parent.absolute())
DATABASE_NAME = 'theapp.db'
DATABASE_PATH = DATBASE_DIR + '/' + DATABASE_NAME

# init Flask app  --------------------------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)




def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
        db.execute('PRAGMA foreign_keys = ON')  # Enable foreign key support
    return db

def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()
        
        
# database structures --------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    key = db.Column(db.Text, nullable=True)
    value = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)

class SharingProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # a person who is sharing
    subscriber_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # a person who is shared
    project_name = db.Column(db.String(100), nullable=False)

        
# template  
# def ...(username, password):
#     conn = get_db()
#     cursor = conn.cursor()
#     close_db()

    
def get_user_value(username, key):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT value
    FROM   user
    WHERE 
        username = ? AND
        key      = ?
    ''', (username, key))
    result = cursor.fetchone()

    cursor.close()
    close_db()    
    return result

def update_user_value(username, key, value):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE user
    SET 
        key = ?,
        value = ?
    WHERE username = ?
''', (key, value, username))
    cursor.commit()
    close_db()    

    
def get_user(username):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM user WHERE username = ?', (username,))
    existing_user = cursor.fetchone()
    close_db()
    
    return existing_user

def create_user(username, password):
    new_project = User(username=username, password=password)
    db.session.add(new_project)
    db.session.commit()
    
    
def get_user_by_password(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
                    SELECT * 
                    FROM user 
                    WHERE 
                        username = ? AND 
                        password = ?
                    ''', (username, password))
    
    user = cursor.fetchone()
    cursor.close()
    close_db()
    return user 

def create_project(project_name, owner_user_id):
    project = SharingProject(project_name=project_name, owner_user_id=owner_user_id)
    db.session.add(project)
    db.session.commit()


def create_project_with_subscribers(project_name, owner_user_id, sub_id):
    project = SharingProject(project_name=project_name, owner_user_id=owner_user_id , subscriber_id = sub_id)
    db.session.add(project)
    db.session.commit()
