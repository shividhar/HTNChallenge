import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, jsonify
import requests
import json


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db/htnChallenge.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/insertToDB')
def add_users():
    userContent = json.loads(requests.get('https://htn-interviews.firebaseio.com/users.json').content)
    db = get_db()
    for user in userContent:
        cur = db.execute('insert into users (name, picture, company, email, phone, country, latitude, longitude) values (?, ?, ?, ?, ?, ?, ?, ?)',
            [user.get("name", None), user.get("picture", None), user.get("company", None), user.get("email", None), user.get("phone", None), user.get("country", None), user.get("latitude", None), user.get("longitude", None)])
        userKey = cur.lastrowid
        for userSkills in user.get("skills"):
            db.execute('insert into skills (id, name, rating) values(?, ?, ?)',
                [userKey, userSkills.get("name"), userSkills.get("rating")])
        
    db.commit()

    # queryUsers = db.execute('select * from users')
    # queryUserSkills = db.execute('select * from skills')
    # for x in queryUserSkills:
    #     print(x)
    # print(queryUsers.fetchone())
    # print(queryUserSkills.fetchone())
    # print(queryUsers.fetchone())
    # print(queryUserSkills.fetchone())
    return "Data Added!"

@app.route('/users')
def sendUsers():
    db = get_db()
    queryUsers = db.execute('select * from users')
    queryUserSkills = db.execute('select * from skills')
    
    returnJson = []
    for user in queryUserSkills:
        currentUser = queryUsers.fetchone()
        skillsJson = []
        if currentUser is not None:
            userSkills = db.execute("select * from skills where id=" + str(currentUser["id"]))
            if userSkills is not None:
                for skill in userSkills:
                    skillsJson.append({
                        "name": skill["name"],
                        "ratin": skill["rating"]
                    })
                returnJson.append({
                    "name": currentUser["name"],
                    "picture": currentUser["picture"],
                    "company": currentUser["company"],
                    "email": currentUser["email"],
                    "phone": currentUser["phone"],
                    "country": currentUser["country"],
                    "latitude": currentUser["latitude"],
                    "longitude": currentUser["longitude"],
                    "skills": skillsJson
                })
    return jsonify(returnJson)

@app.route('/users/<user_id>', methods=["GET"])
def sendUsersById(user_id):
    try:
        user_id = int(user_id)
        db = get_db()
        queryUsersById = db.execute('select * from users where id=' + str(user_id))
        for user in queryUsersById:
            userSkills = db.execute("select * from skills where id=" + str(user["id"]))
            skillsJson = []
            for skill in userSkills:
                skillsJson.append({
                    "name": skill["name"],
                    "rating": skill["rating"]
                })
            returnJson = {
                "name": user["name"],
                "picture": user["picture"],
                "company": user["company"],
                "email": user["email"],
                "phone": user["phone"],
                "country": user["country"],
                "latitude": user["latitude"],
                "longitude": user["longitude"],
                "skills": skillsJson
            }
            return jsonify(returnJson)
        return "USER NOT FOUND"
    except ValueError:
       return "USER NOT FOUND"

@app.route('/users/<user_id>', methods=["PUT"])
def editUser(user_id):
    try:
        user_id = int(user_id)
        changeField = request.args.itervalues().next()
        parameter = request.args.keys()[0]
        if changeField is not None and (parameter == "name" or parameter == "picture" or parameter == "company" or parameter == "email" or parameter == "phone" or parameter == "country" or parameter == "longitude" or parameter == "latitude"):
            if parameter == "latitude" or parameter == "longitude":
                try:
                    changeField = float(changeField)
                except ValueError:
                    return "PASS FLOATING POINT VALUE"
            db = get_db()
            editUserParam = db.execute('update users set ' + parameter + '=\'' + str(changeField) + '\' where id=' + str(user_id))
            db.commit()
            queryUsersById = db.execute('select * from users where id=' + str(user_id))

            for user in queryUsersById:
                userSkills = db.execute("select * from skills where id=" + str(user["id"]))
                skillsJson = []
                for skill in userSkills:
                    skillsJson.append({
                        "name": skill["name"],
                        "rating": skill["rating"]
                    })
                returnJson = {
                    "name": user["name"],
                    "picture": user["picture"],
                    "company": user["company"],
                    "email": user["email"],
                    "phone": user["phone"],
                    "country": user["country"],
                    "latitude": user["latitude"],
                    "longitude": user["longitude"],
                    "skills": skillsJson
                }
                return jsonify(returnJson)

            return "Invalid Parameter"
        return "USER NOT FOUND"
    except ValueError:
       return "USER NOT FOUND"
if __name__ == "__main__":
    app.run();