from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key")
app.permanent_session_lifetime = timedelta(hours=5)

DATABASE = "database.db"

# ---------------------------
# DATABASE
# ---------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            department TEXT,
            phone TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------------------
# ROUTES
# ---------------------------

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session.permanent = True
            session["user"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?,?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            flash("Account created successfully", "success")
            return redirect(url_for("login"))
        except:
            flash("Username already exists", "danger")

    return render_template("register.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

# CONTACTS
@app.route("/contacts", methods=["GET", "POST"])
def contacts():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()

    return render_template("contacts.html", employees=employees)

# ASSISTANT
@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    if "user" not in session:
        return redirect(url_for("login"))

    response = None
    if request.method == "POST":
        question = request.form["question"].lower()

        if "leave" in question:
            response = "Submit leave request in HR portal."
        elif "salary" in question:
            response = "Salary is credited at month end."
        else:
            response = "Please contact HR for more details."

    return render_template("assistant.html", response=response)

# STATUS FORMATTER
@app.route("/status_formatter", methods=["GET", "POST"])
def status_formatter():
    if "user" not in session:
        return redirect(url_for("login"))

    formatted = None
    if request.method == "POST":
        text = request.form["text"]
        formatted = f"Daily Status - {session['user']}\n• {text}"

    return render_template("status_formatter.html", formatted=formatted)

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run()





