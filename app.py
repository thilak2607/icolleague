from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = "super-secret-key"

DATABASE = "icolleague.db"


# ---------------- DATABASE ---------------- #

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]

    if count == 0:
        employees = [
            ('Rajesh Kumar', 'rajesh@techcorp.in', 'Engineering', '+91-98765-43210'),
            ('Priya Sharma', 'priya@techcorp.in', 'HR', '+91-98765-43211'),
            ('Amit Patel', 'amit@techcorp.in', 'Marketing', '+91-98765-43212'),
            ('Anjali Reddy', 'anjali@techcorp.in', 'Finance', '+91-98765-43213')
        ]

        conn.executemany(
            "INSERT INTO employees (name, email, department, phone) VALUES (?, ?, ?, ?)",
            employees
        )

    conn.commit()
    conn.close()


init_db()


# ---------------- ROUTES ---------------- #

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# -------- LOGIN -------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")


# -------- REGISTER -------- #

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed = generate_password_hash(password)

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username already exists", "error")

    return render_template("register.html")


# -------- DASHBOARD -------- #

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])


# -------- CONTACTS -------- #

@app.route("/contacts")
def contacts():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()

    return render_template("contacts.html", employees=employees)


# -------- ASSISTANT -------- #

@app.route("/assistant")
def assistant():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("assistant.html")


@app.route("/ask_assistant", methods=["POST"])
def ask_assistant():
    question = request.form.get("question", "").lower()

    knowledge = {
        "leave": "Submit leave request via HR portal.",
        "salary": "Salary credited last working day of month.",
        "holiday": "Company holidays include national festivals.",
        "it": "Contact IT support at ext. 5557."
    }

    response = "Please contact HR for more details."

    for key in knowledge:
        if key in question:
            response = knowledge[key]
            break

    return jsonify({"response": response})


# -------- STATUS FORMATTER -------- #

@app.route("/status_formatter")
def status_formatter():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("status_formatter.html")


@app.route("/format_status", methods=["POST"])
def format_status():
    text = request.form.get("rough_text", "")

    cleaned = re.sub(r"\s+", " ", text.strip())
    sentences = re.split(r"[.!?]+", cleaned)
    sentences = [s.strip() for s in sentences if s.strip()]

    bullets = "\n".join([f"• {s.capitalize()}." for s in sentences[:5]])

    return jsonify({
        "formatted_status": f"Daily Update - {session['username']}\n\n{bullets}"
    })


# -------- LOGOUT -------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------- RUN -------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)



