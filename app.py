from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'super-secret-key-change-this'

# ---------------- DATABASE ---------------- #

def get_db_connection():
    conn = sqlite3.connect('icolleague.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists('icolleague.db'):
        conn = get_db_connection()

        conn.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

        conn.execute('''
            CREATE TABLE employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                department TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')

        sample_employees = [
            ('Rajesh Kumar', 'rajesh.kumar@techcorp.in', 'Engineering', '+91-98765-43210'),
            ('Priya Sharma', 'priya.sharma@techcorp.in', 'Human Resources', '+91-98765-43211'),
            ('Amit Patel', 'amit.patel@techcorp.in', 'Marketing', '+91-98765-43212'),
        ]

        conn.executemany(
            'INSERT INTO employees (name, email, department, phone) VALUES (?, ?, ?, ?)',
            sample_employees
        )

        conn.commit()
        conn.close()

# IMPORTANT: Run DB init for Render
init_db()

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', 
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')

# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)

        try:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, hashed_password)
            )
            conn.commit()
            conn.close()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')

    return render_template('register.html')

# ---------------- DASHBOARD ---------------- #

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'])

# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

# ---------------- RUN LOCAL ---------------- #

if __name__ == '__main__':
    app.run(debug=True)
