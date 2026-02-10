from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = "super-secret-production-key"

DATABASE = "icolleague.db"


# ================= DATABASE ================= #

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

    # Insert sample data if empty
    count = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]

    if count == 0:
        employees = [
            ('Rajesh Kumar','rajesh@techcorp.in','Engineering','+91-9876543210'),
            ('Priya Sharma','priya@techcorp.in','HR','+91-9876543211'),
            ('Amit Patel','amit@techcorp.in','Marketing','+91-9876543212'),
            ('Anjali Reddy','anjali@techcorp.in','Finance','+91-9876543213'),
            ('Vikram Singh','vikram@techcorp.in','Engineering','+91-9876543214'),
            ('Meera Nair','meera@techcorp.in','Sales','+91-9876543215')
        ]

        conn.executemany("""
        INSERT INTO employees (name,email,department,phone)
        VALUES (?,?,?,?)
        """, employees)

    conn.commit()
    conn.close()


init_db()


# ================= AUTH ================= #

@app.route("/")
def home():
    if "user_id" in session:
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
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login Successful","success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid Credentials","error")

    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("All fields required","error")
            return render_template("register.html")

        hashed = generate_password_hash(password)

        try:
            conn = get_db()
            conn.execute("INSERT INTO users(username,password) VALUES (?,?)",(username,hashed))
            conn.commit()
            conn.close()
            flash("Registration Successful","success")
            return redirect(url_for("login"))
        except:
            flash("Username already exists","error")

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully","info")
    return redirect(url_for("login"))


# ================= DASHBOARD ================= #

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html",username=session["username"])


# ================= CONTACTS ================= #

@app.route("/contacts")
def contacts():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()

    return render_template("contacts.html",employees=employees)


@app.route("/search_contacts",methods=["POST"])
def search_contacts():
    search = request.form.get("search","").lower()

    conn = get_db()
    employees = conn.execute("""
    SELECT * FROM employees
    WHERE LOWER(name) LIKE ?
    OR LOWER(department) LIKE ?
    """,(f"%{search}%",f"%{search}%")).fetchall()
    conn.close()

    return jsonify([dict(row) for row in employees])


# ================= ASSISTANT ================= #

@app.route("/assistant")
def assistant():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("assistant.html")


@app.route("/ask",methods=["POST"])
def ask():
    question = request.form["question"].lower()

    knowledge = {
        "leave":"Submit leave via HR portal.",
        "salary":"Salary credited last working day.",
        "it":"Contact IT at ext 5557.",
        "holiday":"National holidays + festivals.",
        "benefits":"Health insurance + PF included."
    }

    response = "Please contact HR for more info."

    for key in knowledge:
        if key in question:
            response = knowledge[key]
            break

    return jsonify({"response":response})


# ================= STATUS FORMATTER ================= #

@app.route("/status_formatter")
def status_formatter():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("status_formatter.html")


@app.route("/format_status",methods=["POST"])
def format_status():
    text = request.form["text"]
    cleaned = re.sub(r"\s+"," ",text.strip())
    sentences = re.split(r"[.!?]+",cleaned)
    sentences = [s for s in sentences if s]

    bullets = "\n".join([f"• {s.capitalize()}." for s in sentences[:5]])

    return jsonify({
        "formatted":f"Daily Status - {session['username']}\n\n{bullets}"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)




