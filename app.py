from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = "super-secret-key"

DATABASE = "icolleague.db"

# ---------------- DATABASE ---------------- #

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DATABASE):
        conn = get_db()

        conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        conn.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            department TEXT,
            phone TEXT
        )
        """)

        sample = [
            ("Rajesh Kumar","rajesh@techcorp.in","Engineering","+91 9876543210"),
            ("Priya Sharma","priya@techcorp.in","HR","+91 9876543211"),
            ("Amit Patel","amit@techcorp.in","Marketing","+91 9876543212"),
        ]

        conn.executemany("INSERT INTO employees (name,email,department,phone) VALUES (?,?,?,?)", sample)

        conn.commit()
        conn.close()

# ---------------- ROUTES ---------------- #

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
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            conn = get_db()
            conn.execute("INSERT INTO users (username,password) VALUES (?,?)", (username,password))
            conn.commit()
            conn.close()
            flash("Registration successful")
            return redirect(url_for("login"))
        except:
            flash("Username already exists")

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
    return render_template("contacts.html")

@app.route("/search", methods=["POST"])
def search():
    term = request.form.get("term","").lower()
    conn = get_db()
    results = conn.execute(
        "SELECT * FROM employees WHERE LOWER(name) LIKE ? OR LOWER(department) LIKE ?",
        (f"%{term}%", f"%{term}%")
    ).fetchall()
    conn.close()

    return jsonify([dict(r) for r in results])

@app.route("/assistant")
def assistant():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("assistant.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question","").lower()

    answers = {
        "leave": "Apply leave via HR portal.",
        "holiday": "Company holidays include major national festivals.",
        "it": "Contact IT support at ext 5557."
    }

    response = "Please contact HR for more details."

    for key in answers:
        if key in question:
            response = answers[key]

    return jsonify({"response": response})

@app.route("/status_formatter")
def status_formatter():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("status_formatter.html")

@app.route("/format", methods=["POST"])
def format_status():
    text = request.form.get("text","")
    clean = re.sub(r'\s+', ' ', text.strip())
    lines = clean.split(".")
    bullets = "\n".join([f"• {l.strip()}" for l in lines if l.strip()])
    return jsonify({"formatted": bullets})

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)





