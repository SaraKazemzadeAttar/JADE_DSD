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
    project_name = request.cookies.get('project_name')
    
    if value is None:
        if result := get_value_of_project(project_name, username, key):
            response = result[0]
        else:
            response = '{}'
    else:
        update_value_of_project(
            project_name = project_name, 
            username     = username, 
            key          = key, 
            value        = value)
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


@app.route('/share_project', methods=['POST' , 'GET'])
def share_project():
    if request.method == 'POST':
        return redirect(url_for('jade'))

    # Assuming you store the logged-in user's username in the session
    logged_in_username = request.cookies.get('username')

    # Fetch all users except the logged-in user
    users = fetch_users(logged_in_username)

    return render_template('share_project.html', users=users)


@app.route('/skip_project', methods=['GET'])
def skip_project():
    return redirect(url_for('jade'))

    
@app.route('/user_projects', methods=['GET'])
def load_proj():
    username = request.cookies.get('username')
    if username:
        current_user = get_user(username)
        if current_user:
            projects = get_all_projects()
            return render_template("user_projects.html", current_user=current_user, projects=projects)
    return redirect(url_for('login'))

@app.route('/user_projects', methods=['POST'])
def new_project():
    project_name = request.form.get('project_name')
    key = request.form.get('key')
    value = request.form.get('value')
    notification = None

    if "save_project" in request.form:
        if project_name:
            username = request.cookies.get('username')
            user = get_user(username)

            if user:
                existing_project = get_project(project_name , user.id)
                if existing_project:
                    notification = "Project with this name already exists!"
                else:
                    create_project(project_name, user.id, key, value)
                    resp = make_response(redirect(url_for('share_project')))
                    resp.set_cookie('project_name', project_name)
                    return resp

            else:
                return "User not found.", 400
        else:
            return "No project name provided.", 400

    elif "go_to_project" in request.form:
        selected_project_id = request.form.get('project')
        if selected_project_id:
            project = get_project_by_project_id(selected_project_id)
            if project:
                resp = make_response(redirect(url_for('jade', project_id=selected_project_id)))
                resp.set_cookie('project_name', project.project_name)
                return resp
            else:
                return "Project not found.", 400
        else:
            return "No project selected.", 400

    return render_template('user_projects.html', notification=notification)


@app.route('/jade.html')
def jade():
    username = request.cookies.get('username')
    project_id = request.args.get('project_id')

    if username  :
        return render_template('jade.html', project_id=project_id)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)