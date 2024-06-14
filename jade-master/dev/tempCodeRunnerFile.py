@app.route('/share_project', methods=['GET', 'POST'])
def user_projects():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        user_name = request.form.get('username')

        if project_name and user_name:
            user = get_user(user_name)

            if user:
                proj_id = create_empty_project(project_name, user['id'])
                resp = make_response(redirect(url_for('jade')))
                resp.set_cookie('project_id', str(proj_id))
                resp.set_cookie('project_name', project_name)
                return resp
            else:
                return "User not found.", 400
        else:
            return "No project name or username provided.", 400

    return render_template('skip_project.html')