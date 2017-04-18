from flask import Flask
app = Flask(__name__)
from functools import wraps
from flask import request, Response
import csv
import os
import base64
import json
import gpxpy.geo
"""set FLASK_APP=server.py"""
users = {}
classes = {}

def add_to_class(class_id,username):
    i=0
    with open("users.csv",'rb') as f:
       reader = csv.reader(f)
       users = {rows[0]:rows[1:] for rows in reader}
    if username in users:
        if users[username][1] == "s":
            with open(class_id+'.csv', 'rb') as csv_file:
                l = csv_file.readlines()
            l = map(lambda s: s.strip(),l)
            if username not in l:
                l.append(username)
                with open(class_id+'.csv', 'wb') as csv_file:
                    for x in l:
                        csv_file.write(x+"\n")
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
	new_class = open(str(id)+".csv","wb")
	new_class.close()

def class_delete(class_id):
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
    classes.pop(class_id)
    with open('classes.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in classes.items():
            writer.writerow([key, value[0],value[1]])
    try:
        os.remove('D:\\Users\\user-pc\\Desktop\\Python server\\'+class_id+".csv")
    except:
        print "oops"
        return False
    return True

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

@app.route("/send_location")
def location():
    username = request.args.get("username")
    class_name = request.args.get("class_name")
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    print latitude , longitude
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
    for id,names in classes.iteritems():
        if names[0] == class_name: #check if class exists
            with open(id+"class_presence.csv","ab+") as file:
                writer = csv.writer(file)
                writer.writerow([username,latitude,longitude])
            return "GOOD"
    return "ERROR"

@app.route("/check_presence")
def check_presence():
    username = request.args.get("username")
    class_name = request.args.get("class_name")
    latitude = request.args.get("latitude")
    longitude = request.args.get("longitude")
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
    for id,names in classes.iteritems():
        if names[0] == class_name: #check if class exists
            try:
                class_presence = open(id+"class_presence.csv","rb")
                class_presence.close()
            except:
                return "ERROR"
            else:
                userlist = []
                dist = {}
                with open(id+"class_presence.csv","rb") as f:
                    reader = csv.reader(f)
                    presence = {rows[0]:rows[1:] for rows in reader}
                for username,latlon in presence.items():
                    print float(latitude), float(longitude), float(latlon[0]), float(latlon[1])
                    dist[username] = gpxpy.geo.haversine_distance(float(latitude), float(longitude), float(latlon[0]), float(latlon[1]))
                print dist
                for user,d in dist.iteritems():
                    if d > 1:
                        userlist.append(user)
                print userlist
                try:
                    os.remove('D:\Users\user-pc\Desktop\Python server\\'+id+"class_presence.csv")
                except:
                    print "oops"
                else:
                    response = app.response_class(
                    response = json.dumps(userlist),
                    status = 200,
                    mimetype='application/json'
                    )
                    print response,json.dumps(userlist)
                    return response
    return "ERROR"

@app.route("/join_class")
@requires_auth
def join_class():
    class_name = request.args.get("class_name")
    username = request.args.get("username")
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
    for id,names in classes.iteritems():
        if names[0] == class_name:
            if add_to_class(id,username):
                return "GOOD"
                break
    return "ERROR"

@app.route("/quit_class")
@requires_auth
def quit_class():
    class_name = request.args.get("class_name")
    username = request.args.get("username")
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
    for id,names in classes.iteritems():
        if names[0] == class_name:
            if remove_from_class(id,username):
                return "GOOD"
                break
    return "ERROR"

@app.route("/add_class")
@requires_auth
def add_class():
    i=1
    teacher = request.args.get("teacher")
    new_class_name = request.args.get("new_class_name")
    teacher = teacher.encode('ascii','ignore')
    new_class_name = new_class_name.encode('ascii','ignore')
    with open("users.csv",'rb') as f:
        reader = csv.reader(f)
        users = {rows[0]:rows[1:] for rows in reader}
        if teacher in users:
            if users[teacher][1] != "t":
                return "Username not a teacher!"
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
        if new_class_name not in classes.values():
            while True:
                if str(i) not in classes:
                    create_class(teacher,new_class_name,i)
                    return "GOOD"
                    break
                i=i+1
    return "ERROR"

@app.route("/delete_class")
@requires_auth
def delete_class():
    teacher = request.args.get("teacher")
    class_name = request.args.get("class_name")
    teacher = teacher.encode('ascii','ignore')
    class_name = class_name.encode('ascii','ignore')
    with open("users.csv",'rb') as f:
        reader = csv.reader(f)
        users = {rows[0]:rows[1:] for rows in reader}
        if teacher in users:
            if users[teacher][1] != "t":
                return "Username not a teacher!"
    with open("classes.csv",'rb') as f:
        reader = csv.reader(f)
        classes = {rows[0]:rows[1:] for rows in reader}
        for class_id,names in classes.iteritems():
            if names[0] == class_name and names[1] == teacher: #if class exists and teacher is correct
                if class_delete(class_id):
                    return "GOOD"
                break
    return "ERROR"

@app.route('/login')
@requires_auth
def login():
    return "Logged In"

@app.route('/register')
def register():
    username = request.args.get('username')
    password = request.args.get('password')
    permission = request.args.get('permission')
    password = base64.b64decode(password)
    f = open("users.csv",'rb')
    reader = csv.reader(f)
    users = {rows[0]:rows[1:] for rows in reader}
    if username not in users:
        users[username] = [password,permission]
        with open('users.csv', 'wb') as csv_file:
            writer = csv.writer(csv_file)
            for key, value in users.items():
                writer.writerow([key, value[0],value[1]])
        return "GOOD"
    f.close()
    return Response(401)

if __name__ == "__main__":
    app.run()
