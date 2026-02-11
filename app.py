from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

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

    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]

    if count == 0:
        employees = [
            ("Rajesh Kumar","rajesh@techcorp.in","Engineering","+91-9876543210"),
            ("Priya Sharma","priya@techcorp.in","HR","+91-9876543211"),
            ("Amit Patel","amit@techcorp.in","Marketing","+91-9876543212"),
            ("Anjali Reddy","anjali@techcorp.in","Finance","+91-9876543213"),
        ]
        conn.executemany(
            "INSERT INTO employees (name,email,department,phone) VALUES (?,?,?,?)",
            employees
        )

    conn.commit()
    conn.close()


init_db()


# ================= AUTH DECORATOR =================

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first","error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ================= ROUTES =================

@app.route("/")
def home():
    return redirect(url_for("dashboard")) if "user_id" in session else redirect(url_for("login"))


@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?",(username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful!","success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials","error")

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
        except sqlite3.IntegrityError:
            flash("Username already exists","error")

    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session["username"])


@app.route("/contacts", methods=["GET","POST"])
@login_required
def contacts():
    conn = get_db()

    search = request.form.get("search","")
    if search:
        employees = conn.execute("""
            SELECT * FROM employees
            WHERE LOWER(name) LIKE ?
            OR LOWER(department) LIKE ?
        """,(f"%{search.lower()}%",f"%{search.lower()}%")).fetchall()
    else:
        employees = conn.execute("SELECT * FROM employees").fetchall()

    conn.close()

    return render_template("contacts.html", employees=employees)


@app.route("/assistant", methods=["GET","POST"])
@login_required
def assistant():
    response = None

    if request.method == "POST":
        question = request.form["question"].lower()

        knowledge = {
            "leave":"Submit leave request via HR portal.",
            "salary":"Salary credited on last working day.",
            "it":"Contact IT at ext 5557.",
            "holiday":"Check HR portal for holiday calendar."
        }

        response = "Sorry, I don't have information about that."

        for key, value in knowledge.items():
            if key in question:
                response = value
                break

    return render_template("assistant.html", response=response)


@app.route("/status_formatter", methods=["GET","POST"])
@login_required
def status_formatter():
    formatted = None

    if request.method == "POST":
        text = request.form["text"]
        text = re.sub(r'\s+', ' ', text.strip())
        formatted = f"""Daily Status Update - {session['username']}

• {text}

Next Steps:
• Continue assigned tasks
• Resolve blockers
"""

    return render_template("status_formatter.html", formatted=formatted)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)




