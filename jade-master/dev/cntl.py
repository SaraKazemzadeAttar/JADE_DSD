# imports --------------------------------------------
from flask import Flask, request, send_from_directory, jsonify, make_response, redirect, url_for, render_template, abort , g 

import model as m
from model import *
from main import app

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
    username = request.cookies.get('username')
    key = request.form.get('key')
    value = request.form.get('value')

    if value is None:
        if result := get_user_value(username, key):
            response = result[0]
        else:
            response = '{}'
    else:
        update_user_value(username, key, value)
        response = value

    return response

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = m.get_user(username)
        if existing_user:
            return "username already exists!"
        else:
            create_user(username, password)
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = get_user_by_password(username, password)
        if user:
            resp = make_response(redirect(url_for('new_project')))
            resp.set_cookie('username', username)
            return resp
        else:
            return "Invalid credentials! , Correct your password "

    return render_template('login.html')

@app.route('/save_project', methods=['GET'])
def load_proj():
    if request.cookies.get('username'):
        users = User.query.all()
        return render_template('save_project.html', users=users)
    else:
        return redirect(url_for('login'))

@app.route('/save_project', methods=['POST'])
def new_project():
    project_name = request.form.get('project_name')

    if project_name:
        username = request.cookies.get('username')
        user = User.query.filter_by(username=username).first()

        if user:
            new_project = SharingProject(project_name=project_name, owner_user_id=user.id)

            selected_users = request.form.getlist('share_with')

            subscribers = User.query.filter(User.username.in_(selected_users)).all()

            db.session.add(new_project)
            db.session.commit()

            # Save the subscribers to the database
            for subscriber in subscribers:
                new_subscription = SharingProject(owner_user_id=user.id, subscriber_user_id=subscriber.id, project_name=project_name)
                db.session.add(new_subscription)
            db.session.commit()

            resp = make_response(redirect(url_for('jade')))
            resp.set_cookie('project_name', project_name)
            return resp
        else:
            return "User not found.", 400
    else:
        return "No project name provided.", 400


@app.route('/save_project', methods=['POST'])
def save_project():
    share_with = request.form.getlist('share_with')
    project_name = request.form['project_name']
    username = request.cookies.get('username')

    result = get_user(username)
    if result:
        owner_user_id = result[0]
    else:
        return 'User not found.'

    create_project(project_name, owner_user_id)
    for follower_username in share_with:
        result = get_user(follower_username)
        if result:
            sub_user_id = result[0]
            create_project_with_subscribers(project_name,owner_user_id,sub_user_id)
    return 'Project saved successfully!'

@app.route('/skip_project', methods=['GET'])
def skip_project():
    return redirect(url_for('jade'))

     
@app.route('/jade.html')
def jade():
    username = request.cookies.get('username')

    if username  :
        return render_template('jade.html')
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)