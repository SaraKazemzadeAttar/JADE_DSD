from flask import request, send_from_directory, make_response, redirect, url_for, render_template, abort
from model import *
from main import app

# Web routes --------------------------------------------

# ------ base

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
    value = request.form.get('value')
    pid = int(request.cookies.get('project_id'))
    
    if value is None:
        if result := get_project_by_project_id(pid):
            response = result.value
        else:
            response = '{}'
    else:
        update_value_of_project(pid, value)
        response = value
    return response

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/jade.html')
def jade():
    username = request.cookies.get('username')
    if username:
        return render_template('jade.html')
    else:
        return redirect(url_for('index'))

# ------ authentication

@app.route('/signup', methods=['POST'])
def signup_POSTReq():
    username = request.form.get('username')
    password = request.form.get('password')

    existing_user = get_user(username)
    if existing_user:
        return "Username already exists!"
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
        resp = make_response(redirect(url_for('load_project')))
        resp.set_cookie('username', username)
        return resp
    else:
        return "Invalid credentials!"

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# ------ project

# Route to load 'dist.html' and show user projects
@app.route('/dist', methods=['GET'], endpoint='load_project')
def load_project():
    username = request.cookies.get('username')
    current_user = get_user(username)

    if current_user:
        projects = get_all_projects()
        owned_projects = current_user.owned_projects
        shared_projects = current_user.shared_projects

        return render_template("dist.html", 
                               current_user=current_user, 
                               projects=projects, 
                               owned_projects=owned_projects, 
                               shared_projects=shared_projects,
                              )
    else:
        return redirect(url_for('login'))

@app.route('/share_project', methods=['GET'])
def share_project():
    logged_in_username = request.cookies.get('username')

    if not logged_in_username:
        return redirect(url_for('login'))

    users = all_users()
    return render_template('share_project.html', users=users, your_username=logged_in_username)

@app.route('/share_project', methods=['POST'])
def user_projects():
    project_name = request.form.get('project_name')
    user_name = request.cookies.get('username')
    project_id = int(request.cookies.get('project_id'))

    if project_name and user_name:
        user = get_user(user_name)

        if user:
            proj = get_project_by_project_id(project_id)
            if not proj:
                return "Project not found.", 400

            selected_user_ids = request.form.getlist('share_with[]')
            subscribers = get_user_by_ids(selected_user_ids)
            subscribe_to_proj(proj, subscribers)

            resp = make_response(redirect(url_for('jade')))
            return resp
        else:
            return "User not found.", 400
    else:
        return render_template('skip_project.html')

    
@app.route('/skip_project', methods=['GET'])
def skip_project():
    return redirect(url_for('jade'))

@app.route('/user_projects', methods=['GET'])
def load_proj():
    username = request.cookies.get('username')
    current_user = get_user(username)
    
    if current_user:
        projects = get_all_projects()
        owned_projects = current_user.owned_projects
        shared_projects = current_user.shared_projects
        return render_template("user_projects.html", 
                               current_user=current_user, 
                               projects=projects, 
                               owned_projects=owned_projects, 
                               shared_projects=shared_projects)
    else:
        return redirect(url_for('login'))

@app.route('/user_projects', methods=['POST'])
def new_project():
    notification = None
    project_name = request.form.get('project_name')

    if "save_project" in request.form and project_name:
        username = request.cookies.get('username')
        user = get_user(username)

        if user:
            existing_project = get_project(project_name, user.id)
            if existing_project:
                notification = "Project with this name already exists!"
            else:
                proj_id = create_empty_project(project_name, user.id)
                resp = make_response(redirect(url_for('share_project')))
                resp.set_cookie('project_id', str(proj_id))
                resp.set_cookie('project_name', project_name) 
                return resp
        else:
            return "User not found.", 400
    else:
        return "No project name provided.", 400

    return render_template('user_projects.html', notification=notification)

# Route to set a specific project for viewing
@app.route('/set_project/<project_name>/<int:owner_id>', methods=['GET'])
def set_project(project_name, owner_id):
    proj = get_project(project_name, owner_id)
    if proj:
        resp = make_response(redirect(url_for('jade')))  # Assuming 'jade' is a placeholder
        resp.set_cookie('project_id', str(proj.id))
        resp.set_cookie('project_name', project_name)  # Set project name in cookie
        return resp
    else:
        return "Project not found.", 404

# ------ entry point
if __name__ == '__main__':
    app.run(debug=True, port=5000)
