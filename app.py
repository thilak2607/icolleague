# app.py - Simple Working Version
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'simple-secret-key-123'

# Simple in-memory database
users = {
    "rajesh@company.com": {
        "id": 1,
        "password": "password123",
        "name": "Rajesh Kumar",
        "role": "Software Engineer",
        "department": "IT",
        "avatar": "👨‍💻"
    },
    "priya@company.com": {
        "id": 2,
        "password": "password123",
        "name": "Priya Sharma",
        "role": "HR Manager",
        "department": "HR",
        "avatar": "👩‍💼"
    }
}

tasks = [
    {"id": 1, "title": "Complete report", "assignee": "Rajesh Kumar", "status": "Pending", "due": "Today"},
    {"id": 2, "title": "Team meeting", "assignee": "Rajesh Kumar", "status": "In Progress", "due": "Tomorrow"},
    {"id": 3, "title": "Code review", "assignee": "Rajesh Kumar", "status": "Completed", "due": "Yesterday"}
]

meetings = [
    {"id": 1, "title": "Daily Standup", "time": "10:30 AM", "link": "https://zoom.us/j/123"},
    {"id": 2, "title": "Client Call", "time": "2:00 PM", "link": "https://zoom.us/j/456"}
]

holidays = [
    {"date": "Mar 25", "name": "Holi", "type": "Public Holiday"},
    {"date": "Apr 11", "name": "Ramzan", "type": "Public Holiday"},
    {"date": "May 1", "name": "May Day", "type": "Public Holiday"}
]

# Routes
@app.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and users[email]['password'] == password:
            session['user_email'] = email
            session['user_name'] = users[email]['name']
            session['user_role'] = users[email]['role']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users:
            return render_template('register.html', error="Email already registered")
        
        # Add new user
        users[email] = {
            "id": len(users) + 1,
            "password": password,
            "name": name,
            "role": "Employee",
            "department": "General",
            "avatar": "👤"
        }
        
        session['user_email'] = email
        session['user_name'] = name
        session['user_role'] = "Employee"
        
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    user = users.get(user_email, {})
    
    # Get user-specific tasks
    user_tasks = [t for t in tasks if t['assignee'] == user.get('name', '')]
    
    return render_template('dashboard.html',
                         user=user,
                         tasks=user_tasks,
                         meetings=meetings,
                         holidays=holidays[:2],
                         today=datetime.now().strftime("%A, %d %B %Y"))

@app.route('/assistant')
def assistant():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    user = users.get(user_email, {})
    
    return render_template('assistant.html', user=user)

@app.route('/contacts')
def contacts():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    user = users.get(user_email, {})
    
    # Get all users except current user
    contacts_list = [u for u in users.values() if u['name'] != user.get('name', '')]
    
    return render_template('contacts.html', 
                         user=user,
                         contacts=contacts_list,
                         departments=["IT", "HR", "Sales", "Marketing"])

# API Endpoints
@app.route('/api/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = 'Completed'
            return jsonify({'success': True, 'task': task})
    return jsonify({'success': False}), 404

@app.route('/api/attendance/punch', methods=['POST'])
def punch_attendance():
    return jsonify({
        'success': True,
        'message': 'Attendance recorded',
        'time': datetime.now().strftime("%I:%M %p")
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').lower()
    
    responses = {
        'hello': "Hello! How can I help you today?",
        'hi': "Hi there! What can I do for you?",
        'leave': "You can apply for leave from the dashboard. You have 12 leaves remaining.",
        'holiday': "Next holiday is Holi on March 25th.",
        'task': f"You have {len([t for t in tasks if t['status'] != 'Completed'])} pending tasks.",
        'meeting': f"You have {len(meetings)} meetings today.",
        'expense': "Submit expenses from the expenses page. Make sure to attach receipts.",
        'help': "I can help with: leaves, tasks, meetings, expenses, and general queries."
    }
    
    response = responses.get(message, "I'm here to help! Ask me about leaves, tasks, or meetings.")
    
    return jsonify({
        'success': True,
        'response': response
    })

if __name__ == '__main__':
    # Ensure templates directory exists
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🚀 Starting iColleague...")
    print("🌐 Open: http://localhost:5000")
    print("📧 Login with: rajesh@company.com / password123")
    print("📧 Or register a new account")
    
    app.run(debug=True, port=5000)
