from flask import request, send_from_directory, make_response, redirect, url_for, render_template, abort
from model import *
from main import app


# ------ project
@app.route('/dist', methods=['GET'])
def load_proj():
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




