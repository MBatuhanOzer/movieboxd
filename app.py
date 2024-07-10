import datetime
import pytz
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
                rows = cursor.execute("SELECT * FROM users WHERE username = ?", (name,)).fetchall()
                rad = [dict(row) for row in rows]
                if len(rad) != 0:
                    flash("User already exists")
                    return redirect("/login")
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
    return render_template("index.html")


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
    rowswl = cursor.execute("SELECT * FROM watchlist WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid)).fetchall()
    watch_list = [dict(row) for row in rowswl]
    rowswd = cursor.execute("SELECT * FROM watched WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid)).fetchall()
    watch_ed = [dict(row) for row in rowswd]
    if len(watch_ed) == 1:
        watched = True
    else: 
        watched = False
    if len(watch_list) == 1:
        watchlist = True
    else:
        watchlist = False
    return render_template("movie.html", watched=watched, watchlist=watchlist)
    


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
    rowswl = cursor.execute("SELECT * FROM watchlist WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid)).fetchall()
    watch_list = [dict(row) for row in rowswl]
    rowswd = cursor.execute("SELECT * FROM watched WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid)).fetchall()
    watch_ed = [dict(row) for row in rowswd]
    t = datetime.datetime.now(pytz.timezone("Turkey")).strftime('%Y-%m-%d %H:%M:%S')
    if button == "watched":
        if len(watch_ed) == 1:
            cursor.execute("DELETE FROM watched WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid))
            conn.commit()
            return "Deleted"
        elif len(watch_ed) == 0:
            cursor.execute("INSERT INTO watched (user_id, movie_id, time) VALUES (?, ?, ?)", (session["user_id"], movieid, t))
            conn.commit()
            if len(watch_list) == 1:
                cursor.execute("DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid))
                conn.commit()
                return "Watched from watchlist"
            return "Added to watched"        
    elif button == "watchlist":
        if len(watch_list) == 1:
            cursor.execute("DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?", (session["user_id"],movieid))
            conn.commit()
            return "Deleted"
        elif len(watch_list) == 0:
            cursor.execute("INSERT INTO watchlist (user_id, movie_id, time) VALUES (?, ?, ?)",(session["user_id"], movieid, t))
            conn.commit()
            return "Added to watchlist"


@app.route("/watchlist", methods=["GET"])
@login_required
def watchlist():
    global API
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM watchlist WHERE user_id = ? ORDER BY time DESC", (session["user_id"],)).fetchall()
    rad = [dict(row) for row in rows]
    movies = []
    for movie in rad:
        query = movie["movie_id"]
        response = requests.get(f'https://api.themoviedb.org/3/movie/{query}',params={
        'api_key': API
    })
        if response.status_code == 200:
            movie_data = response.json()
            movies.append(movie_data)
        else:
            print(f"Error fetching data for movie ID {movie['movie_id']}: {response.status_code}")
    length = len(movies)
    return render_template("watch.html", movies=movies, title="Watchlist", len=length)


@app.route("/watched", methods=["GET"])
@login_required
def watched():
    global API
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM watched WHERE user_id = ? ORDER BY time DESC", (session["user_id"],)).fetchall()
    rad = [dict(row) for row in rows]
    movies = []
    for movie in rad:
        query = movie["movie_id"]
        response = requests.get(f'https://api.themoviedb.org/3/movie/{query}',params={
        'api_key': API
    })
        if response.status_code == 200:
            movie_data = response.json()
            movies.append(movie_data)
        else:
            print(f"Error fetching data for movie ID {movie['movie_id']}: {response.status_code}")
    length = len(movies)
    return render_template("watch.html", movies=movies, title="Watched", len=length)




