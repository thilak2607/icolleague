# app.py - Complete Enterprise Employee Portal
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
import json
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'icolleague-enterprise-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database Simulation
class EmployeeDB:
    def __init__(self):
        self.users = self.load_users()
        self.employees = self.load_employees()
        self.tasks = self.load_tasks()
        self.meetings = self.load_meetings()
        self.projects = self.load_projects()
        self.holidays = self.load_holidays()
        self.expenses = self.load_expenses()
        self.attendance = self.load_attendance()
        self.announcements = self.load_announcements()
        self.chat_messages = []
        
    def load_users(self):
        return {
            "rajesh@company.com": {
                "id": 1,
                "password": generate_password_hash("password123"),
                "employee_id": "EMP001",
                "role": "employee"
            },
            "priya@company.com": {
                "id": 2,
                "password": generate_password_hash("password123"),
                "employee_id": "EMP002",
                "role": "hr"
            },
            "admin@company.com": {
                "id": 3,
                "password": generate_password_hash("admin123"),
                "employee_id": "ADMIN001",
                "role": "admin"
            }
        }
    
    def load_employees(self):
        return [
            {
                "id": 1,
                "emp_id": "EMP001",
                "name": "Rajesh Kumar",
                "email": "rajesh@company.com",
                "role": "Senior Software Engineer",
                "department": "IT",
                "phone": "+91 9876543210",
                "location": "Bangalore",
                "avatar": "👨‍💻",
                "status": "Available",
                "skills": ["Python", "Flask", "React", "AWS"],
                "performance": 94,
                "manager": "Priya Sharma",
                "joining_date": "2020-06-15",
                "birthday": "1990-08-20",
                "employee_type": "Full-time",
                "salary_band": "L4",
                "work_location": "Office",
                "shift": "9:30 AM - 6:30 PM",
                "leaves_balance": {
                    "casual": 12,
                    "sick": 10,
                    "earned": 15,
                    "maternity": 0
                }
            },
            {
                "id": 2,
                "emp_id": "EMP002",
                "name": "Priya Sharma",
                "email": "priya@company.com",
                "role": "HR Manager",
                "department": "Human Resources",
                "phone": "+91 9876543211",
                "location": "Mumbai",
                "avatar": "👩‍💼",
                "status": "In Meeting",
                "skills": ["Recruitment", "Employee Relations", "Payroll"],
                "performance": 91,
                "manager": "Amit Patel",
                "joining_date": "2018-03-22",
                "birthday": "1988-11-15",
                "employee_type": "Full-time",
                "salary_band": "L5"
            },
            {
                "id": 3,
                "emp_id": "EMP003",
                "name": "Arun Singh",
                "email": "arun@company.com",
                "role": "Sales Executive",
                "department": "Sales",
                "phone": "+91 9876543212",
                "location": "Delhi",
                "avatar": "👨‍💼",
                "status": "On Field",
                "skills": ["Sales", "CRM", "Negotiation"],
                "performance": 87,
                "manager": "Neha Gupta",
                "joining_date": "2021-01-10",
                "birthday": "1992-03-30",
                "employee_type": "Full-time",
                "salary_band": "L3"
            }
        ]
    
    def load_tasks(self):
        return [
            {
                "id": 1,
                "title": "Complete Banking Portal UAT",
                "description": "Perform User Acceptance Testing for new internet banking portal",
                "project": "Digital Banking",
                "assignee": "Rajesh Kumar",
                "assignee_id": 1,
                "priority": "High",
                "status": "In Progress",
                "due_date": "2024-03-15",
                "estimated_hours": 40,
                "actual_hours": 25,
                "progress": 62,
                "tags": ["Testing", "Banking", "UAT"],
                "created_by": "Priya Sharma",
                "created_date": "2024-02-20",
                "last_updated": "2024-03-05"
            },
            {
                "id": 2,
                "title": "Prepare Q1 Sales Report",
                "description": "Compile and analyze sales data for Q1 FY2024",
                "project": "Sales Analytics",
                "assignee": "Arun Singh",
                "assignee_id": 3,
                "priority": "Medium",
                "status": "Pending",
                "due_date": "2024-03-10",
                "estimated_hours": 20,
                "actual_hours": 0,
                "progress": 0,
                "tags": ["Sales", "Reporting", "Analysis"],
                "created_by": "Neha Gupta",
                "created_date": "2024-03-01",
                "last_updated": "2024-03-01"
            },
            {
                "id": 3,
                "title": "Update Employee Handbook",
                "description": "Revise company policies and update employee handbook",
                "project": "HR Operations",
                "assignee": "Priya Sharma",
                "assignee_id": 2,
                "priority": "Low",
                "status": "Completed",
                "due_date": "2024-02-28",
                "estimated_hours": 15,
                "actual_hours": 18,
                "progress": 100,
                "tags": ["HR", "Documentation", "Policy"],
                "created_by": "Amit Patel",
                "created_date": "2024-02-01",
                "last_updated": "2024-02-28"
            }
        ]
    
    def load_meetings(self):
        return [
            {
                "id": 1,
                "title": "Daily Standup - Development Team",
                "description": "Daily progress update and blocker discussion",
                "type": "Daily Scrum",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": "10:30 AM",
                "duration": "30 mins",
                "organizer": "Priya Sharma",
                "participants": ["Rajesh Kumar", "Arun Singh", "Amit Patel", "Neha Gupta"],
                "location": "Conference Room 3 (Virtual)",
                "agenda": ["Sprint Progress Review", "Blockers Discussion", "Today's Tasks"],
                "zoom_link": "https://zoom.us/j/1234567890",
                "status": "upcoming",
                "recording_url": ""
            },
            {
                "id": 2,
                "title": "Client Presentation - ICICI Bank",
                "description": "Demo of new banking features to client",
                "type": "Client Meeting",
                "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                "time": "2:00 PM",
                "duration": "2 hours",
                "organizer": "Arun Singh",
                "participants": ["Rajesh Kumar", "Priya Sharma", "Neha Gupta"],
                "location": "ICICI Bank HQ, Mumbai",
                "agenda": ["Project Demo", "Requirements Discussion", "Timeline Review"],
                "zoom_link": "",
                "status": "scheduled",
                "recording_url": ""
            },
            {
                "id": 3,
                "title": "Monthly Performance Review",
                "description": "Quarterly performance assessment and feedback",
                "type": "Review Meeting",
                "date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
                "time": "11:00 AM",
                "duration": "1 hour",
                "organizer": "Amit Patel",
                "participants": ["Rajesh Kumar", "Priya Sharma"],
                "location": "Manager's Cabin",
                "agenda": ["Performance Review", "Goal Setting", "Feedback Session"],
                "zoom_link": "https://zoom.us/j/0987654321",
                "status": "scheduled",
                "recording_url": ""
            }
        ]
    
    def load_projects(self):
        return [
            {
                "id": 1,
                "name": "Digital Banking Platform",
                "code": "DBP-2024",
                "client": "State Bank of India",
                "description": "Development of next-gen internet banking platform",
                "start_date": "2023-12-01",
                "end_date": "2024-06-30",
                "budget": "₹2.5 Crores",
                "status": "Active",
                "progress": 65,
                "manager": "Priya Sharma",
                "team": ["Rajesh Kumar", "Arun Singh", "Amit Patel"],
                "technologies": ["Java", "React", "Oracle", "AWS"],
                "risks": "Medium",
                "milestones": [
                    {"name": "Requirement Analysis", "completed": True},
                    {"name": "Design Phase", "completed": True},
                    {"name": "Development", "completed": False},
                    {"name": "Testing", "completed": False},
                    {"name": "Deployment", "completed": False}
                ]
            },
            {
                "id": 2,
                "name": "GST Compliance System",
                "code": "GCS-2024",
                "client": "Reliance Industries",
                "description": "Automated GST filing and compliance system",
                "start_date": "2024-01-15",
                "end_date": "2024-12-31",
                "budget": "₹1.8 Crores",
                "status": "Planning",
                "progress": 20,
                "manager": "Amit Patel",
                "team": ["Arun Singh", "Priya Sharma"],
                "technologies": ["Python", "Django", "PostgreSQL", "Docker"],
                "risks": "Low",
                "milestones": [
                    {"name": "Requirement Analysis", "completed": True},
                    {"name": "Design Phase", "completed": False},
                    {"name": "Development", "completed": False},
                    {"name": "Testing", "completed": False},
                    {"name": "Deployment", "completed": False}
                ]
            }
        ]
    
    def load_holidays(self):
        return [
            {"date": "2024-03-25", "name": "Holi", "type": "Public Holiday", "description": "Festival of Colors"},
            {"date": "2024-04-09", "name": "Ugadi", "type": "Regional Holiday", "description": "Telugu New Year"},
            {"date": "2024-04-11", "name": "Ramzan", "type": "Public Holiday", "description": "Eid al-Fitr"},
            {"date": "2024-05-01", "name": "May Day", "type": "Public Holiday", "description": "Labour Day"},
            {"date": "2024-08-15", "name": "Independence Day", "type": "Public Holiday", "description": "Indian Independence Day"},
            {"date": "2024-10-02", "name": "Gandhi Jayanti", "type": "Public Holiday", "description": "Mahatma Gandhi's Birthday"},
            {"date": "2024-10-23", "name": "Diwali", "type": "Public Holiday", "description": "Festival of Lights"}
        ]
    
    def load_expenses(self):
        return [
            {
                "id": 1,
                "date": "2024-03-01",
                "category": "Travel",
                "description": "Flight Delhi to Bangalore",
                "amount": 8500.00,
                "currency": "INR",
                "gst_amount": 1530.00,
                "total_amount": 10030.00,
                "status": "Approved",
                "receipt": "air_india_123.pdf",
                "project": "Digital Banking",
                "approved_by": "Priya Sharma",
                "approved_date": "2024-03-02",
                "reimbursement_date": "2024-03-05"
            },
            {
                "id": 2,
                "date": "2024-03-02",
                "category": "Food",
                "description": "Client Dinner at Taj Hotel",
                "amount": 12300.00,
                "currency": "INR",
                "gst_amount": 2214.00,
                "total_amount": 14514.00,
                "status": "Pending",
                "receipt": "taj_bill.pdf",
                "project": "Client Meeting",
                "approved_by": "",
                "approved_date": "",
                "reimbursement_date": ""
            },
            {
                "id": 3,
                "date": "2024-03-03",
                "category": "Accommodation",
                "description": "Hotel stay for client visit",
                "amount": 7500.00,
                "currency": "INR",
                "gst_amount": 1350.00,
                "total_amount": 8850.00,
                "status": "Submitted",
                "receipt": "hotel_invoice.pdf",
                "project": "Sales Analytics",
                "approved_by": "",
                "approved_date": "",
                "reimbursement_date": ""
            }
        ]
    
    def load_attendance(self):
        return [
            {
                "date": "2024-03-01",
                "day": "Friday",
                "status": "Present",
                "check_in": "09:15 AM",
                "check_out": "06:30 PM",
                "location": "Office",
                "hours_worked": 9.25,
                "overtime": 0.25,
                "late_entry": False,
                "early_exit": False
            },
            {
                "date": "2024-03-02",
                "day": "Saturday",
                "status": "WFH",
                "check_in": "09:30 AM",
                "check_out": "06:45 PM",
                "location": "Home",
                "hours_worked": 9.25,
                "overtime": 0.25,
                "late_entry": False,
                "early_exit": False
            },
            {
                "date": "2024-03-04",
                "day": "Monday",
                "status": "Present",
                "check_in": "09:45 AM",
                "check_out": "06:15 PM",
                "location": "Office",
                "hours_worked": 8.5,
                "overtime": 0,
                "late_entry": True,
                "early_exit": False
            }
        ]
    
    def load_announcements(self):
        return [
            {
                "id": 1,
                "title": "New Office Timings",
                "content": "Effective March 15, office timings will be 9:30 AM to 6:30 PM",
                "author": "HR Department",
                "date": "2024-03-01",
                "priority": "High",
                "category": "Policy Change"
            },
            {
                "id": 2,
                "title": "Team Lunch - Friday",
                "content": "Team lunch this Friday at 1 PM in the cafeteria",
                "author": "Priya Sharma",
                "date": "2024-03-04",
                "priority": "Medium",
                "category": "Team Event"
            },
            {
                "id": 3,
                "title": "IT Maintenance",
                "content": "Scheduled IT maintenance on Saturday from 10 PM to 2 AM",
                "author": "IT Department",
                "date": "2024-03-03",
                "priority": "Low",
                "category": "Maintenance"
            }
        ]

# Initialize database
db = EmployeeDB()

# Authentication middleware
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = db.users.get(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_email'] = email
            session['user_role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        employee_id = request.form.get('employee_id')
        
        if email in db.users:
            flash('Email already registered', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        else:
            # In real app, this would be validated against HR records
            user_id = max([u['id'] for u in db.users.values()]) + 1
            db.users[email] = {
                'id': user_id,
                'password': generate_password_hash(password),
                'employee_id': employee_id,
                'role': 'employee'
            }
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    employee = next((e for e in db.employees if e['email'] == session.get('user_email')), db.employees[0])
    
    # Filter tasks for current employee
    employee_tasks = [t for t in db.tasks if t['assignee_id'] == employee['id']]
    
    # Filter meetings for current employee
    employee_meetings = []
    for meeting in db.meetings:
        if employee['name'] in meeting['participants']:
            employee_meetings.append(meeting)
    
    # Calculate stats
    stats = {
        'total_tasks': len(employee_tasks),
        'completed_tasks': len([t for t in employee_tasks if t['status'] == 'Completed']),
        'pending_tasks': len([t for t in employee_tasks if t['status'] in ['Pending', 'In Progress']]),
        'today_meetings': len([m for m in employee_meetings if m['date'] == datetime.now().strftime("%Y-%m-%d")]),
        'total_projects': len([p for p in db.projects if employee['name'] in p['team']]),
        'leave_balance': employee['leaves_balance']['casual'] + employee['leaves_balance']['sick'] + employee['leaves_balance']['earned']
    }
    
    # Get recent activity
    recent_activity = [
        {"type": "task_update", "task": "Banking Portal UAT", "time": "2 hours ago", "status": "In Progress"},
        {"type": "meeting", "title": "Daily Standup", "time": "Today, 10:30 AM", "status": "Completed"},
        {"type": "expense", "title": "Travel Expense", "time": "Yesterday", "status": "Approved"},
        {"type": "announcement", "title": "New Office Timings", "time": "2 days ago", "status": "New"}
    ]
    
    return render_template('dashboard.html',
                         employee=employee,
                         tasks=employee_tasks[:5],
                         meetings=employee_meetings[:3],
                         announcements=db.announcements[:3],
                         stats=stats,
                         recent_activity=recent_activity,
                         current_date=datetime.now().strftime("%A, %d %B %Y"),
                         weather={"temp": 22, "condition": "Sunny"})

@app.route('/assistant')
@login_required
def assistant():
    employee = next((e for e in db.employees if e['email'] == session.get('user_email')), db.employees[0])
    return render_template('assistant.html', employee=employee)

@app.route('/contacts')
@login_required
def contacts():
    employee = next((e for e in db.employees if e['email'] == session.get('user_email')), db.employees[0])
    return render_template('contacts.html', 
                         employees=db.employees,
                         employee=employee,
                         departments=["IT", "HR", "Sales", "Finance", "Marketing"])

@app.route('/expenses')
@login_required
def expenses():
    employee = next((e for e in db.employees if e['email'] == session.get('user_email')), db.employees[0])
    
    # Filter expenses for current employee
    employee_expenses = [e for e in db.expenses]
    
    # Calculate summary
    summary = {
        'total': sum(e['total_amount'] for e in employee_expenses),
        'approved': sum(e['total_amount'] for e in employee_expenses if e['status'] == 'Approved'),
        'pending': sum(e['total_amount'] for e in employee_expenses if e['status'] == 'Pending'),
        'reimbursed': sum(e['total_amount'] for e in employee_expenses if e['status'] == 'Approved' and e['reimbursement_date'])
    }
    
    return render_template('expense.html',
                         employee=employee,
                         expenses=employee_expenses,
                         summary=summary,
                         categories=["Travel", "Food", "Accommodation", "Office Supplies", "Equipment"])

@app.route('/holidays')
@login_required
def holidays():
    employee = next((e for e in db.employees if e['email'] == session.get('user_email')), db.employees[0])
    
    # Get next 3 holidays
    today = datetime.now().strftime("%Y-%m-%d")
    upcoming_holidays = [h for h in db.holidays if h['date'] >= today][:3]
    
    # Group by month
    holidays_by_month = {}
    for holiday in db.holidays:
        month = datetime.strptime(holiday['date'], "%Y-%m-%d").strftime("%B %Y")
        if month not in holidays_by_month:
            holidays_by_month[month] = []
        holidays_by_month[month].append(holiday)
    
    return render_template('holidays.html',
                         employee=employee,
                         holidays=db.holidays,
                         upcoming_holidays=upcoming_holidays,
                         holidays_by_month=holidays_by_month)

# API Endpoints
@app.route('/api/attendance/punch', methods=['POST'])
@login_required
def punch_attendance():
    employee = next((e for e in db.employees if e['email'] == session.get('user_email')), None)
    
    if employee:
        today = datetime.now().strftime("%Y-%m-%d")
        punch_type = request.json.get('type', 'check_in')
        
        # Simulate attendance record
        attendance_record = {
            "date": today,
            "day": datetime.now().strftime("%A"),
            "status": "Present",
            "check_in": datetime.now().strftime("%I:%M %p"),
            "check_out": "",
            "location": request.json.get('location', 'Office'),
            "hours_worked": 0,
            "overtime": 0,
            "late_entry": False,
            "early_exit": False
        }
        
        db.attendance.append(attendance_record)
        
        return jsonify({
            'success': True,
            'message': f'Attendance {punch_type} recorded',
            'timestamp': datetime.now().isoformat(),
            'employee': employee['name']
        })
    
    return jsonify({'success': False, 'message': 'Employee not found'}), 404

@app.route('/api/tasks/update', methods=['POST'])
@login_required
def update_task():
    data = request.json
    task_id = data.get('task_id')
    status = data.get('status')
    
    # Find and update task
    for task in db.tasks:
        if task['id'] == task_id:
            task['status'] = status
            task['last_updated'] = datetime.now().strftime("%Y-%m-%d")
            
            if status == 'Completed':
                task['progress'] = 100
                task['actual_hours'] = task['estimated_hours']
            
            return jsonify({'success': True, 'task': task})
    
    return jsonify({'success': False, 'message': 'Task not found'}), 404

@app.route('/api/expenses/submit', methods=['POST'])
@login_required
def submit_expense():
    data = request.json
    
    new_expense = {
        "id": max([e['id'] for e in db.expenses]) + 1,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": data.get('category'),
        "description": data.get('description'),
        "amount": float(data.get('amount', 0)),
        "currency": "INR",
        "gst_amount": float(data.get('amount', 0)) * 0.18,
        "total_amount": float(data.get('amount', 0)) * 1.18,
        "status": "Pending",
        "receipt": data.get('receipt', ''),
        "project": data.get('project', ''),
        "approved_by": "",
        "approved_date": "",
        "reimbursement_date": ""
    }
    
    db.expenses.append(new_expense)
    
    return jsonify({'success': True, 'expense': new_expense})

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_chat():
    data = request.json
    message = data.get('message')
    sender = session.get('user_email')
    
    chat_message = {
        'id': len(db.chat_messages) + 1,
        'sender': sender,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'type': 'user'
    }
    
    db.chat_messages.append(chat_message)
    
    # Generate AI response (simplified)
    if 'leave' in message.lower():
        response = "I can help with leave applications. You have 12 casual leaves, 10 sick leaves, and 15 earned leaves remaining."
    elif 'expense' in message.lower():
        response = "You can submit expenses through the Expenses page. Make sure to attach receipts."
    elif 'task' in message.lower():
        response = "You have 3 pending tasks. Check your dashboard for details."
    else:
        response = "I'm here to help! You can ask about leaves, expenses, tasks, or meetings."
    
    ai_response = {
        'id': len(db.chat_messages) + 1,
        'sender': 'iColleague Assistant',
        'message': response,
        'timestamp': datetime.now().isoformat(),
        'type': 'ai'
    }
    
    db.chat_messages.append(ai_response)
    
    return jsonify({'success': True, 'response': ai_response})

@app.route('/api/weather')
@login_required
def get_weather():
    # Simulated weather API
    weather_conditions = ['Sunny', 'Partly Cloudy', 'Cloudy', 'Rainy', 'Stormy']
    return jsonify({
        'temperature': random.randint(18, 32),
        'condition': random.choice(weather_conditions),
        'humidity': random.randint(40, 80),
        'wind_speed': random.randint(5, 20)
    })

# WebSocket events
@socketio.on('connect')
def handle_connect():
    if 'user_email' in session:
        emit('user_connected', {
            'user': session['user_email'],
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if 'user_email' in session:
        emit('user_disconnected', {
            'user': session['user_email'],
            'timestamp': datetime.now().isoformat()
        }, broadcast=True)

@socketio.on('send_message')
def handle_socket_message(data):
    emit('receive_message', {
        'user': data['user'],
        'message': data['message'],
        'timestamp': datetime.now().isoformat()
    }, broadcast=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
