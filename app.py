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


with open("api.txt", "r") as file:
    API = file.readline()

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
            rows = cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)).fetchall()
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
    global API
    response = requests.get(f'https://api.themoviedb.org/3/movie/popular', params={
        'api_key': API,
        'language': 'en-US',
        'page': 1
    })
    if response.status_code == 200:
        return render_template("index.html", movies=response.json().get("results", []))
    return []


@app.route('/search', methods=['GET'])
@login_required
def search():
    global API
    query = request.args.get('q')
    if query:
        response = requests.get(f'https://api.themoviedb.org/3/search/movie', params={
            'api_key': API,
            'query': query
        })
        data = response.json()
        return jsonify(data)
    return jsonify({'results': []})


@app.route("/movie/<int:movieid>")
@login_required
def movie(movieid):
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM movies WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid))
    rad = [dict(row) for row in rows]
    if len(rad) == 1:
        match rad[0]["status"]:
            case "watched and watchlist":
                return render_template("movie.html", watched=True, watchlist=True)
            case "watched":
                return render_template("movie.html", watched=True, watchlist=False)
            case "watchlist":
                return render_template("movie.html", watched=False, watchlist=True)
    else:
        return render_template("movie.html", watched=False, watchlist=False)

@app.route("/api", methods=["GET"])
@login_required
def api():
    global API
    query = request.args.get('q')
    response = requests.get(f'https://api.themoviedb.org/3/movie/{query}',params={
        'append_to_response': 'videos',
        'api_key': API
    })
    return jsonify(response.json())

@app.route("/change/<int:movieid>/<string:button>")
@login_required
def change(movieid, button):
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM movies WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid))
    rad = [dict(row) for row in rows]
    if len(rad) == 1:
        if button == "watched":
            if rad[0]["status"] == "watched":
                cursor.execute("DELETE FROM movies WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid))
                conn.commit()
                return "Deleted"
            if rad[0]["status"] == "watchlist":
                cursor.execute("UPDATE movies SET status = ? WHERE user_id = ? AND movie_id = ?", ("watched",session["user_id"],movieid))
                conn.commit()
                return "Watched from watchlist"
            if rad[0]["status"] == "watched and watchlist":
                cursor.execute("UPDATE movies SET status = ? WHERE user_id = ? AND movie_id = ?", ("watchlist",session["user_id"],movieid))
                conn.commit()
                return "Deleted"
        if button == "watchlist":
            if rad[0]["status"] == "watched":
                cursor.execute("UPDATE movies SET status = ? WHERE user_id = ? AND movie_id = ?", ("watched and watchlist",session["user_id"],movieid))
                conn.commit()
                return "Added to watchlist"
            if rad[0]["status"] == "watchlist":
                cursor.execute("DELETE FROM movies WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid))
                conn.commit()
                return "Deleted"
            if rad[0]["status"] == "watched and watchlist":
                cursor.execute("UPDATE movies SET status = ? WHERE user_id = ? AND movie_id = ?", ("watched",session["user_id"],movieid))
                conn.commit()
                return "Deleted"
    else:
        if button == "watched":
            cursor.execute("INSERT INTO movies (status, user_id, movie_id) VALUES (?, ?, ?)", ("watched",session["user_id"],movieid))
            conn.commit()
            return "Added to watched"
        if button == "watchlist":
            cursor.execute("INSERT INTO movies (status, user_id, movie_id) VALUES (?, ?, ?)", ("watchlist",session["user_id"],movieid))
            conn.commit()
            return "Added to watchlist"