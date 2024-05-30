from flask import abort, Flask, request, send_from_directory, jsonify, make_response, redirect, url_for, render_template
import os
import json

app = Flask(__name__,template_folder='.', static_url_path='', static_folder='')
jsonfile = 'labs.json'

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

    if not os.path.exists(jsonfile):
        with open(jsonfile, 'w') as f:
            json.dump({}, f)

    with open(jsonfile, 'r') as f:
        labs = json.load(f)

    if value is None:
        response = labs.get(key, '{}')
    else:
        labs[key] = value
        with open(jsonfile, 'w') as f:
            json.dump(labs, f)
        response = value

    return response

if __name__ == '__main__':
    app.run(port=8000, debug=True)