from flask import Flask
app = Flask(__name__)
from functools import wraps
from flask import request, Response
import csv
"""set FLASK_APP=server.py"""
users = {}
classes = {}

def add_to_class(class_id,username):
    with open("users.csv",'rb') as f:
       reader = csv.reader(f)
       users = {rows[0]:rows[1:] for rows in reader}
    if username in users:
        if users[username][1] == "s":
            with open(class_id+".csv",'ab') as f:
                f.write(username+"\n") 
                return True
    return False

def remove_from_class(class_id,username):
    with open("users.csv",'rb') as f:
       reader = csv.reader(f)
       users = {rows[0]:rows[1:] for rows in reader}
    if username in users:
        if users[username][1] == "s":
            with open(class_id+'.csv', 'rb') as csv_file:
                l = csv_file.readlines()
            l = map(lambda s: s.strip(),l)
            if username in l:
                l.remove(username)
                with open(class_id+'.csv', 'wb') as csv_file:
                    for x in l:
                        csv_file.write(x+"\n")
                return True
    return False

def create_class(teacher,class_name,id):
    f = open("classes.csv",'rb')
    reader = csv.reader(f)
    classes = {rows[0]:rows[1:] for rows in reader}
    f.close()
    classes[id] = [class_name,teacher]
    print classes
    with open('classes.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in classes.items():
            writer.writerow([key, value[0],value[1]])
	new_class = open(str(id)+".scv","wb")
	new_class.close()

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    the csv file is converted to a dictionary (user:pass,t/s)
    """
    with open("users.csv",'rb') as f:
       reader = csv.reader(f)
       users = {rows[0]:rows[1:] for rows in reader}
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
    return "WELCOME!    to login: /login    to join a class: /join_class"

@app.route("/join_class")
@requires_auth
def join_class():
    class_id = request.args.get("class_id")
    username = request.args.get("username")
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
    if class_id in classes:
        if add_to_class(class_id,username)==True:
            return "GOOD"
    return "ERROR"

@app.route("/quit_class")
@requires_auth
def quit_class():
    class_id = request.args.get("class_id")
    username = request.args.get("username")
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
    if class_id in classes:
        if remove_from_class(class_id,username):
            return "GOOD"
    return "ERROR"

@app.route("/add_class")
@requires_auth
def add_class():
    i=1
    teacher = request.args.get("teacher")
    new_class_name = request.args.get("new_class_name")
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
        if new_class_name not in classes.values():
            while True:
                if str(i) not in classes:
                    teacher = teacher.encode('ascii','ignore')
                    new_class_name = new_class_name.encode('ascii','ignore')
                    create_class(teacher,new_class_name,i)
                    return "GOOD"
                    break
                i=i+1
    return "ERROR"

@app.route('/login')
@requires_auth
def login():
    return "Logged In"

if __name__ == "__main__":
    app.run()
