from flask import Flask
app = Flask(__name__)
from functools import wraps
from flask import request, Response
import csv


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    with open('users.csv') as users_file:
        reader = csv.reader(users_file)
        users = {}
        for row in reader:
            key = row[0]
            if key in users:
                # implement your duplicate row handling here
                pass
            users[key] = row[1:]
    if username in users:
        if users[username][0] == password:
            return True
    return False

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/join_group")
@requires_auth
def join_group():
    group_id = request.args.get("group_id")
    if group_id == "17":
	    return "good"
    else:
        return group_id

@app.route('/secret-page')
@requires_auth
def secret_page():
    return "good"
	
if __name__ == "__main__":
    app.run()
