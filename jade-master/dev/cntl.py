# imports --------------------------------------------
from flask import Flask, request, send_from_directory, jsonify, make_response, redirect, url_for, render_template, abort , g 
from json import loads

import model as m
from model import *
from main import app

from json import loads, dumps
from pprint import pprint

# web routes  --------------------------------------------

@app.route('/<path:path>', methods=['GET'])
def serve_static(path):
    if not path:
        path = 'index.html'
    try:
        return send_from_directory('.', path)
    except FileNotFoundError:
        abort(404)
        
@app.route('/', methods=['POST'])
def handle_post():
    key = request.form.get('key')
    value = request.form.get('value')
    username = request.cookies.get('username')
    project_name = request.form.get('project_name')
    
    if value is None:
        if result := get_value_of_project(project_name, username, key):
            response = result[0]
        else:
            response = '{}'
    else:
        update_value_of_project(project_name, username, key, value)
        response = value

    return response

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def signup_POSTReq():
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = get_user(username)
        if existing_user:
            return "username already exists!"
        else:
            create_user(username, password)
            return redirect(url_for('login'))

@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@app.route('/login', methods=['POST'])
def login_POSTReq():
        username = request.form['username']
        password = request.form['password']

        user = get_user_by_password(username, password)
        if user:
            resp = make_response(redirect(url_for('new_project')))
            resp.set_cookie('username', username)
            return resp
        else:
            return "Invalid credentials! "

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

    
@app.route('/user_projects', methods=['GET'])
def load_proj():
    if request.cookies.get('username'):
        current_user = User.query.filter_by(username=request.cookies.get('username')).first()
        if current_user:
            projects = Project.query.all()
            return render_template("user_projects.html", current_user=current_user, projects=projects)
    return redirect(url_for('login'))

@app.route('/user_projects', methods=['POST'])
def new_project():
    project_name = request.form.get('project_name')
    key = request.form.get('key')
    value = request.form.get('value')

    if project_name:
        username = request.cookies.get('username')
        user = User.query.filter_by(username=username).first()

        if user:
            create_project(project_name, user.id , key , value)
            resp = make_response(redirect(url_for('jade')))
            resp.set_cookie('project_name', project_name)
            return resp
        else:
            return "User not found.", 400
    else:
        return "No project name provided.", 400
    

@app.route('/jade.html')
def jade():
    username = request.cookies.get('username')

    if username  :
        return render_template('jade.html')
    else:
        return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.run(debug=True, port=5000)