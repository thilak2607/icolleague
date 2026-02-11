# app.py
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_caching import Cache
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import random
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Indian Database
class IndianVirtualDB:
    def __init__(self):
        self.employees = self.load_indian_employees()
        self.tasks = self.load_indian_tasks()
        self.meetings = self.load_indian_meetings()
        self.projects = self.load_indian_projects()
        self.holidays = self.load_indian_holidays()
        self.expenses = self.load_indian_expenses()
        self.attendance = self.load_attendance()
    
    def load_indian_employees(self):
        return [
            {
                "id": 1,
                "emp_id": "TATA001",
                "name": "Rajesh Kumar",
                "role": "Senior Software Engineer",
                "department": "IT",
                "email": "rajesh.kumar@tatadigital.com",
                "phone": "+91-9876543210",
                "location": "Bangalore, Karnataka",
                "avatar": "👨‍💻",
                "status": "active",
                "skills": ["Java", "Spring Boot", "Microservices", "AWS"],
                "performance": 94,
                "salary_band": "L4",
                "manager": "Priya Sharma",
                "joining_date": "2020-06-15",
                "employee_type": "Full-time"
            },
            {
                "id": 2,
                "emp_id": "INF002",
                "name": "Priya Sharma",
                "role": "Project Manager",
                "department": "Management",
                "email": "priya.sharma@infosys.com",
                "phone": "+91-9876543211",
                "location": "Hyderabad, Telangana",
                "avatar": "👩‍💼",
                "status": "in-meeting",
                "skills": ["Agile", "Scrum", "JIRA", "Stakeholder Management"],
                "performance": 91,
                "salary_band": "L5",
                "manager": "Amit Patel",
                "joining_date": "2018-03-22",
                "employee_type": "Full-time"
            },
            {
                "id": 3,
                "emp_id": "WIP003",
                "name": "Arun Singh",
                "role": "Sales Executive",
                "department": "Sales & Marketing",
                "email": "arun.singh@wipro.com",
                "phone": "+91-9876543212",
                "location": "Mumbai, Maharashtra",
                "avatar": "👨‍💼",
                "status": "on-field",
                "skills": ["Sales", "CRM", "Negotiation", "Market Analysis"],
                "performance": 87,
                "salary_band": "L3",
                "manager": "Neha Gupta",
                "joining_date": "2021-01-10",
                "employee_type": "Full-time"
            },
            {
                "id": 4,
                "emp_id": "HCL004",
                "name": "Deepika Iyer",
                "role": "HR Manager",
                "department": "Human Resources",
                "email": "deepika.iyer@hcl.com",
                "phone": "+91-9876543213",
                "location": "Chennai, Tamil Nadu",
                "avatar": "👩‍🎓",
                "status": "available",
                "skills": ["Talent Acquisition", "Employee Relations", "Payroll", "Training"],
                "performance": 89,
                "salary_band": "L5",
                "manager": "Rahul Verma",
                "joining_date": "2019-08-30",
                "employee_type": "Full-time"
            }
        ]
    
    def load_indian_tasks(self):
        return [
            {
                "id": 1,
                "title": "Complete UAT for Banking Portal",
                "description": "User Acceptance Testing for new internet banking portal",
                "priority": "High",
                "status": "In Progress",
                "assignee": "Rajesh Kumar",
                "due_date": "2024-03-15",
                "project": "Digital Banking",
                "estimated_hours": 40,
                "actual_hours": 25,
                "tags": ["Testing", "Banking", "UAT"]
            },
            {
                "id": 2,
                "title": "Prepare Quarterly Sales Report",
                "description": "Compile sales data for Q1 FY2024 and present to management",
                "priority": "Medium",
                "status": "Pending",
                "assignee": "Arun Singh",
                "due_date": "2024-03-10",
                "project": "Sales Analytics",
                "estimated_hours": 20,
                "actual_hours": 0,
                "tags": ["Sales", "Reporting", "Analysis"]
            }
        ]
    
    def load_indian_meetings(self):
        return [
            {
                "id": 1,
                "title": "Daily Standup - Bengaluru Team",
                "type": "Daily Scrum",
                "date": "2024-03-05",
                "time": "10:30 AM",
                "duration": "30 mins",
                "participants": ["Rajesh Kumar", "Priya Sharma", "Amit Patel"],
                "location": "Conference Room 3 (Virtual)",
                "agenda": ["Sprint Progress", "Blockers", "Today's Plan"],
                "zoom_link": "https://zoom.us/j/1234567890"
            },
            {
                "id": 2,
                "title": "Client Presentation - ICICI Bank",
                "type": "Client Meeting",
                "date": "2024-03-06",
                "time": "2:00 PM",
                "duration": "2 hours",
                "participants": ["Arun Singh", "Neha Gupta", "Rajesh Kumar"],
                "location": "ICICI Bank HQ, Mumbai",
                "agenda": ["Project Demo", "Requirements Discussion", "Next Steps"],
                "zoom_link": ""
            }
        ]
    
    def load_indian_projects(self):
        return [
            {
                "id": 1,
                "name": "Digital Banking Platform",
                "client": "State Bank of India",
                "start_date": "2023-12-01",
                "end_date": "2024-06-30",
                "budget": "₹2.5 Crores",
                "status": "Active",
                "progress": 65,
                "team": ["Rajesh Kumar", "Priya Sharma", "Amit Patel"],
                "technologies": ["Java", "React", "Oracle", "AWS"]
            },
            {
                "id": 2,
                "name": "GST Compliance System",
                "client": "Reliance Industries",
                "start_date": "2024-01-15",
                "end_date": "2024-12-31",
                "budget": "₹1.8 Crores",
                "status": "Planning",
                "progress": 20,
                "team": ["Arun Singh", "Deepika Iyer"],
                "technologies": ["Python", "Django", "PostgreSQL", "Docker"]
            }
        ]
    
    def load_indian_holidays(self):
        return [
            {"date": "2024-03-25", "name": "Holi", "type": "Public Holiday"},
            {"date": "2024-04-09", "name": "Ugadi", "type": "Regional Holiday"},
            {"date": "2024-04-11", "name": "Ramzan", "type": "Public Holiday"},
            {"date": "2024-05-01", "name": "May Day", "type": "Public Holiday"},
            {"date": "2024-08-15", "name": "Independence Day", "type": "Public Holiday"},
            {"date": "2024-10-02", "name": "Gandhi Jayanti", "type": "Public Holiday"},
            {"date": "2024-10-23", "name": "Diwali", "type": "Public Holiday"}
        ]
    
    def load_indian_expenses(self):
        return [
            {
                "id": 1,
                "date": "2024-03-01",
                "category": "Travel",
                "description": "Flight Delhi to Bangalore",
                "amount": "₹8,500",
                "status": "Approved",
                "receipt": "air_india_123.pdf"
            },
            {
                "id": 2,
                "date": "2024-03-02",
                "category": "Food",
                "description": "Client Dinner at Taj Hotel",
                "amount": "₹12,300",
                "status": "Pending",
                "receipt": "taj_bill.pdf"
            }
        ]
    
    def load_attendance(self):
        return [
            {
                "date": "2024-03-01",
                "status": "Present",
                "check_in": "09:15 AM",
                "check_out": "06:30 PM",
                "location": "Office"
            },
            {
                "date": "2024-03-02",
                "status": "WFH",
                "check_in": "09:30 AM",
                "check_out": "06:45 PM",
                "location": "Home"
            }
        ]

db = IndianVirtualDB()

# Routes
@app.route('/')
def home():
    return render_template('dashboard.html', 
                         employee=db.employees[0],
                         tasks=db.tasks,
                         meetings=db.meetings[:3],
                         holidays=db.holidays[:3],
                         projects=db.projects)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html',
                         employee=db.employees[0],
                         tasks=db.tasks,
                         meetings=db.meetings,
                         holidays=db.holidays,
                         projects=db.projects)

@app.route('/employee/<int:emp_id>')
def employee_profile(emp_id):
    employee = next((e for e in db.employees if e['id'] == emp_id), None)
    if employee:
        return render_template('employee_profile.html',
                             employee=employee,
                             attendance=db.attendance,
                             expenses=db.expenses)
    return redirect('/')

@app.route('/tasks')
def tasks_view():
    return render_template('tasks.html',
                         tasks=db.tasks,
                         employees=db.employees)

@app.route('/meetings')
def meetings_view():
    return render_template('meetings.html',
                         meetings=db.meetings)

@app.route('/projects')
def projects_view():
    return render_template('projects.html',
                         projects=db.projects)

@app.route('/holidays')
def holidays_view():
    return render_template('holidays.html',
                         holidays=db.holidays)

@app.route('/attendance')
def attendance_view():
    return render_template('attendance.html',
                         attendance=db.attendance,
                         employee=db.employees[0])

@app.route('/expenses')
def expenses_view():
    return render_template('expenses.html',
                         expenses=db.expenses)

# API Endpoints
@app.route('/api/employees', methods=['GET'])
def get_employees():
    return jsonify(db.employees)

@app.route('/api/tasks/update', methods=['POST'])
def update_task():
    data = request.json
    task_id = data.get('task_id')
    status = data.get('status')
    # Update task logic here
    return jsonify({"success": True, "message": "Task updated"})

@app.route('/api/attendance/punch', methods=['POST'])
def punch_attendance():
    data = request.json
    # Attendance punching logic
    return jsonify({"success": True, "timestamp": datetime.now().isoformat()})

@app.route('/api/expenses/submit', methods=['POST'])
def submit_expense():
    data = request.json
    # Expense submission logic
    return jsonify({"success": True, "expense_id": len(db.expenses) + 1})

# SocketIO for real-time features
@socketio.on('connect')
def handle_connect():
    emit('status_update', {'message': 'Connected to iColleague'})

@socketio.on('send_message')
def handle_message(data):
    emit('receive_message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
