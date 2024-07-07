import sqlite3
import requests
from flask import Flask, redirect, render_template, request, session, flash, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def api():
    with open("api.txt", "r") as file:
        return file.readline()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if session.get("user_id") != None:
        return redirect("/")
    else:
        if request.method == "POST":

            if not request.form.get("username"):
                flash("Provide a username")
                return redirect("/login")
            if not request.form.get("password"):
                flash("Enter your password")
                return redirect("/login")
            rows =cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()
            rad = [dict(row) for row in rows]
            if len(rad) != 1:
                flash("Invalid username")
                return redirect("/login")
            if check_password_hash(rad[0]["hash"], request.form.get("password")):
                flash("Invalid password")
                return redirect("/login")
            session["user_id"] = rad[0]["id"]
            return redirect("/")
        
        else:
            return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if session.get("user_id") != None:
        return redirect("/")
    else:
        if request.method == "POST":

            if not request.form.get("username"):
                flash("Provide a username")
                return redirect("/register")
            if not request.form.get("password"):
                flash("Enter your password")
                return redirect("/register")
            if not request.form.get("confirmation"):
                flash("Confirm your password")
                return redirect("/register")
            if request.form.get("password") != request.form.get("confirmation"):
                flash("Passwords don't match")
                return redirect("/register")

            try:
                name = request.form.get("username")
                passhash = generate_password_hash(request.form.get("password"))
                cursor.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (name, passhash,))
                conn.commit()
                userid = cursor.execute("SELECT id FROM users WHERE username = ?", (name,)).fetchall()
                rad = [dict(row) for row in userid]
                session["user_id"] = rad[0]["id"]
                return redirect("/")
        # Displays an error message for already existing users.
            except ValueError:
                flash("User already exists")
                return redirect("/login")
        
        else:
            return render_template("register.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/login")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    MOVIE_DB_API_KEY = api()
    if query:
        response = requests.get(f'https://api.themoviedb.org/3/search/movie', params={
            'api_key': MOVIE_DB_API_KEY,
            'query': query
        })
        data = response.json()
        return jsonify(data)
    return jsonify({'results': []})

