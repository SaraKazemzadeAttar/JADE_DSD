# imports --------------------------------------------
from flask import Flask, request, send_from_directory, jsonify, make_response, redirect, url_for, render_template, abort , g 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlite3, os

# constants --------------------------------------------

# python3.10 -m flask --app test db init
# python3.10 -m flask --app test db merge
# python3.10 -m flask --app test db upgrade
# python3.10 -m flask --app test db migrate
# python3.10 -m flask --app test db upgrade


DAATBASE_DIR =  os.getcwd()
DATABASE_NAME = 'theapp.db'
DATABASE_PATH = DAATBASE_DIR + '/' + DATABASE_NAME

print(DATABASE_PATH)

app = Flask(__name__, template_folder='.', static_url_path='', static_folder='')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DATABASE_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask & database interactions --------------------------------------------

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

# init Flask app  --------------------------------------------

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# database structures --------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    key = db.Column(db.Text, nullable=True)
    value = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    # followers = db.relationship('SharingProject', backref='user', lazy=True)

class SharingProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    
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

    conn = get_db()
    cursor = conn.cursor()

    if value is None:
        # Check if the user is associated with the project
        cursor.execute('''
            SELECT value
            FROM   user
            WHERE 
                username = ? AND
                key      = ?
        ''', (username, key))
        result = cursor.fetchone()
        if result:
            response = result[0]
        else:
            response = '{}'
    else:
        # insert or update value
        cursor.execute('''
            UPDATE user
            SET 
                key = ?,
                value = ?
            WHERE username = ?
        ''', (key, value, username))
        conn.commit()
        response = value

    cursor.close()
    close_db()

    return response

@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User WHERE username = ?', (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            return "username already exists!"
        else:
            cursor.execute('INSERT INTO User (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            cursor.close()
            close_db()
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
                       SELECT * 
                       FROM User 
                       WHERE 
                            username = ? AND 
                            password = ?
                       ''', (username, password))
        user = cursor.fetchone()

        if user:
            resp = make_response(redirect(url_for('new_project')))
            resp.set_cookie('username', username)
            close_db()
            return resp
        else:
            return "Invalid credentials! , Correct your password "

    return render_template('login.html')

@app.route('/save_project', methods=['GET', 'POST'])
def new_project():
    print("11111111111111111")
    if request.method == 'POST':
        project_name = request.form.get('project_name')

        if project_name:
            username = request.cookies.get('username')
            user = User.query.filter_by(username=username).first()

            if user:
                new_project = SharingProject(project_name=project_name, user_id=user.id)
                db.session.add(new_project)
                db.session.commit()

                return redirect(url_for('jade'))
            else:
                return "User not found.", 400
        else:
            return "No project name provided.", 400
    else:
        print("22222222222222222")
        
        if request.cookies.get('username'):
            print("3333333333333333333")
            users = User.query.all()
            print("4444444444444444444")
            return render_template('save_project.html', users=users)
        else:
            print("5555555555555555555")
            return redirect(url_for('login'))

@app.route('/save_project', methods=['POST'])
def save_project():
    share_with = request.form.getlist('share_with')
    project_name = request.form['project_name']
    password = request.cookies.get('password')

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM User WHERE password = ?', (password,))
    result = cursor.fetchone()
    if result:
        user_id = result[0]
    else:
        return 'User not found.'

    cursor.execute('INSERT INTO SharingProject(user_id, project_name) VALUES (?, ?)', (user_id, project_name))
    conn.commit()

    for follower_username in share_with:
        cursor.execute('SELECT id FROM User WHERE username = ?', (follower_username,))
        result = cursor.fetchone()
        if result:
            follower_user_id = result[0]
            cursor.execute('INSERT INTO SharingProject (user_id , project_name) VALUES (?, ?)', (user_id, follower_user_id))
            conn.commit()

    cursor.close()
    close_db()

    return 'Project saved successfully!'


@app.route('/skip_project', methods=['GET'])
def skip_project():
    return redirect(url_for('jade'))


@app.route('/jade.html')
def jade():
    username = request.cookies.get('username')
    password = request.cookies.get('password')

    if username  :
        return render_template('jade.html')
    else:
        return redirect(url_for('index'))
    
# building CRUD ---------------------------------------------------

# Create a new Database
@app.route('/Databases', methods=['POST'])
def create_Database():
    title = request.form.get('title')
    completed = request.form.get('completed')

    new_Database = User(title=title, completed=completed)
    db.session.add(new_Database)
    db.session.commit()

    return jsonify({'message': 'Database created successfully'})

# Read all Databases
@app.route('/Databases', methods=['GET'])
def get_Databases():
    Databases = User.query.all()
    result = [
        {'id': User.id, 'title': User.title, 'completed': User.completed}
        for _ in Databases
    ]
    return jsonify(result)

# Read a specific Database
@app.route('/Databases/<int:Database_id>', methods=['GET'])
def get_Database(Database_id):
    Database = User.query.get(Database_id)
    if Database:
        result = {'id': Database.id, 'title': Database.title, 'completed': Database.completed}
        return jsonify(result)
    else:
        return jsonify({'message': 'Database not found'})

# Update a Database
@app.route('/Databases/<int:Database_id>', methods=['PUT'])
def update_Database(Database_id):
    Database = Database.query.get(Database_id)
    if Database:
        title = request.form.get('title')
        completed = request.form.get('completed')

        Database.title = title if title else Database.title
        Database.completed = completed if completed else Database.completed

        db.session.commit()

        return jsonify({'message': 'Database updated successfully'})
    else:
        return jsonify({'message': 'Database not found'})

# Delete a Database
@app.route('/Databases/<int:Database_id>', methods=['DELETE'])
def delete_Database(Database_id):
    Database = Database.query.get(Database_id)
    if Database:
        db.session.delete(Database)
        db.session.commit()
        return jsonify({'message': 'Database deleted successfully'})
    else:
        return jsonify({'message': 'Database not found'})
    

@app.route("/Databases/create", methods=["POST"])
def create():
    title = request.form.get("title")
    new_Database = User(title=title, completed=False)
    db.session.add(new_Database)
    db.session.commit()
    return redirect(url_for("get_tasks"))
      
# entry point  --------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, port=8000)