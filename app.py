import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
condition = [False]

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index(try_login=False):
    title = "Home"
    return render_template("index.html", title=title, condition = condition[-1], try_login=try_login)

@app.route("/logout")
def logout():
    condition.append(False)
    return index()   

@app.route("/login", methods=["POST"])
def login():
    username_fill = request.form.get("username")
    password_fill = request.form.get("password")
    users = db.execute("SELECT USERNAME, PASSWORD FROM users")
    usernames = []
    passwords = []
    for user in users:
        username = user.username
        usernames.append(username)
        password = user.password
        passwords.append(password)

    if(username_fill in usernames):
        if(passwords[usernames.index(username_fill)] == password_fill):
            condition.append(True)
            return index()
        else:
            return index(try_login=True)
    else:
        return index(try_login=True)
   

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    db.execute("INSERT INTO users(USERNAME, PASSWORD) VALUES (:username, :password)",
                {"username" : username, "password" : password})
    db.commit()
    return index()

@app.route("/database")
def more():
    title = "Database"
    users = db.execute("SELECT USERNAME, PASSWORD FROM users")
    usernames = []
    passwords = []
    for user in users:
        username = user.username
        usernames.append(username)
        password = user.password
        passwords.append(password)
    return render_template("more.html", title=title, condition=condition[-1], usernames=usernames, passwords=passwords)

        


