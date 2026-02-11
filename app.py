from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = "super-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "icolleague.db")


# ================= DATABASE =================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
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

    # Insert sample employees if empty
    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if count == 0:
        sample = [
            ("Rajesh Kumar","rajesh@company.com","Engineering","+91-9876543210"),
            ("Priya Sharma","priya@company.com","HR","+91-9876543211"),
            ("Amit Patel","amit@company.com","Marketing","+91-9876543212"),
        ]
        conn.executemany(
            "INSERT INTO employees (name,email,department,phone) VALUES (?,?,?,?)",
            sample
        )

    conn.commit()
    conn.close()


init_db()


# ================= ROUTES =================

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?",(username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            flash("Login successful!","success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password","error")

    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username,password) VALUES (?,?)",(username,password))
            conn.commit()
            conn.close()
            flash("Registration successful!","success")
            return redirect(url_for("login"))
        except:
            flash("Username already exists","error")

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["user"])


@app.route("/contacts")
def contacts():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()

    return render_template("contacts.html", employees=employees)


@app.route("/assistant", methods=["GET","POST"])
def assistant():
    if "user" not in session:
        return redirect(url_for("login"))

    response = None

    if request.method == "POST":
        question = request.form["question"].lower()

        knowledge = {
            "leave":"Submit leave via HR portal.",
            "salary":"Salary credited last working day.",
            "it":"Contact IT at ext 5557.",
            "holiday":"Check HR portal for holidays."
        }

        response = "I don't have info about that."

        for key in knowledge:
            if key in question:
                response = knowledge[key]
                break

    return render_template("assistant.html", response=response)


@app.route("/status_formatter", methods=["GET","POST"])
def status_formatter():
    if "user" not in session:
        return redirect(url_for("login"))

    formatted = None

    if request.method == "POST":
        text = request.form["text"]
        text = re.sub(r'\s+', ' ', text.strip())
        formatted = f"Daily Status - {session['user']}\n• {text}"

    return render_template("status_formatter.html", formatted=formatted)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)


