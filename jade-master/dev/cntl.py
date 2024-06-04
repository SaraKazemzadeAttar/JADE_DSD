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

    if value is None:
        if result := get_user_value(username, key):
            response = result[0]
        else:
            response ='{}'
    else:
        update_user_value(username, key, value)
        response = value

    return response


@app.route('/@<username>/<project_name>', methods=['POST'])
def handle_sharing_post(username, project_name):
    key = request.form.get('key')
    value = request.form.get('value')
    if value is None:
        if result := get_user_value_of_shared_project(project_name, username, key):
            response = result[0]
        else:
            response = '{}'
    else:
        update_user_value_of_shared_project(project_name, username, key, value)
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
            return "Invalid credentials! , Correct your password "

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

    
@app.route('/save_project', methods=['GET'])
def load_proj():
    if request.cookies.get('username'):
        # Assuming the 'username' cookie corresponds to the logged-in user's username
        current_user = User.query.filter_by(username=request.cookies.get('username')).first()
        if current_user:
            # Fetch all users and shared projects
            users = User.query.all()
            users_shared = SharingProject.query.all()
            # Pass the current user object and lists to the template
            return render_template("save_project.html", users=users, current_user=current_user, users_shared=users_shared)
    return redirect(url_for('login'))

@app.route('/save_project', methods=['POST'])
def new_project():
    project_name = request.form.get('project_name')

    if project_name:
        username = request.cookies.get('username')
        user = User.query.filter_by(username=username).first()

        if user:
            create_project(project_name, user.id)
            selected_users = request.form.getlist('share_with')
            subscribers = User.query.filter(User.username.in_(selected_users)).all()
            for subscriber in subscribers:
                create_project_with_subscribers(project_name, user.id, subscriber.id)
                owner_username = user.username 
                handle_sharing_post(owner_username, project_name)
            resp = make_response(redirect(url_for('jade')))
            resp.set_cookie('project_name', project_name)
            return resp
        else:
            return "User not found.", 400
    else:
        return "No project name provided.", 400

@app.route('/skip_project', methods=['GET'])
def skip_project():
    resp = make_response(redirect(url_for('jade')))
    # Set the 'project_name' cookie to expire immediately to effectively delete it
    resp.set_cookie('project_name', '', max_age=0)
    return resp

@app.route('/jade.html')
def jade():
    username = request.cookies.get('username')

    if username  :
        return render_template('jade.html')
    else:
        return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.run(debug=True, port=5000)
