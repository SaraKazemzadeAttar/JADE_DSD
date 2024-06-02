@app.route('/save_project', methods=['POST'])
def new_project():
    project_name = request.form.get('project_name')

    if project_name:
        username = request.cookies.get('username')
        user = User.query.filter_by(username=username).first()

        if user:
            selected_users = request.form.getlist('share_with')
            subscribers = User.query.filter(User.username.in_(selected_users)).all()

            create_project(project_name, user.id)

            for subscriber in subscribers:
                create_project_with_subscribers(project_name, user.id, subscriber.id)

            resp = make_response(redirect(url_for('jade')))
            resp.set_cookie('project_name', project_name)
            return resp
        else:
            return "User not found.", 400
    else:
        return "No project name provided.", 400