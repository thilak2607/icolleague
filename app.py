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
    conn = get_db_connection()

    # Create users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create employees table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            department TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')

    # Insert sample employees only if table empty
    existing = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]

    if existing == 0:
        sample_employees = [
            ('Rajesh Kumar', 'rajesh.kumar@techcorp.in', 'Engineering', '+91-98765-43210'),
            ('Priya Sharma', 'priya.sharma@techcorp.in', 'Human Resources', '+91-98765-43211'),
            ('Amit Patel', 'amit.patel@techcorp.in', 'Marketing', '+91-98765-43212'),
            ('Anjali Reddy', 'anjali.reddy@techcorp.in', 'Finance', '+91-98765-43213'),
        ]

        conn.executemany(
            'INSERT INTO employees (name, email, department, phone) VALUES (?, ?, ?, ?)',
            sample_employees
        )

    conn.commit()
    conn.close()

# Initialize database ALWAYS (important for Render)
init_db()

# ---------------- ROUTES ---------------- #

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required', 'error')
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


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])


@app.route('/contacts')
def contacts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('contacts.html')


@app.route('/assistant')
def assistant():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('assistant.html')


@app.route('/status_formatter')
def status_formatter():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('status_formatter.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


# ---------------- API ROUTES ---------------- #

@app.route('/search_contacts', methods=['POST'])
def search_contacts():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    search_term = request.form.get('search_term', '').lower()
    conn = get_db_connection()

    employees = conn.execute(
        'SELECT * FROM employees WHERE LOWER(name) LIKE ? OR LOWER(department) LIKE ?',
        (f'%{search_term}%', f'%{search_term}%')
    ).fetchall()

    conn.close()

    return jsonify([
        {
            'name': emp['name'],
            'email': emp['email'],
            'department': emp['department'],
            'phone': emp['phone']
        }
        for emp in employees
    ])


@app.route('/ask_assistant', methods=['POST'])
def ask_assistant():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    question = request.form.get('question', '').lower()

    knowledge_base = {
        'leave': 'Submit leave request through HR portal.',
        'it': 'Contact IT support at it-support@techcorp.in',
        'holiday': 'Company holidays include Republic Day, Diwali, Christmas.'
    }

    for keyword, answer in knowledge_base.items():
        if keyword in question:
            return jsonify({'response': answer})

    return jsonify({'response': "Please contact HR for more details."})


@app.route('/format_status', methods=['POST'])
def format_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    rough_text = request.form.get('rough_text', '')
    cleaned = re.sub(r'\s+', ' ', rough_text.strip())

    return jsonify({
        'formatted_status': f"Daily Status - {session['username']}\n\n• {cleaned}"
    })


# ---------------- RUN LOCAL ---------------- #

if __name__ == '__main__':
    app.run(debug=True)
