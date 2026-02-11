
Here's the complete code for the Indian version of iColleague:

## **app.py**
```python
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

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
            ('Anjali Reddy', 'anjali.reddy@techcorp.in', 'Finance', '+91-98765-43213'),
            ('Vikram Singh', 'vikram.singh@techcorp.in', 'Engineering', '+91-98765-43214'),
            ('Meera Nair', 'meera.nair@techcorp.in', 'Sales', '+91-98765-43215'),
            ('Suresh Iyer', 'suresh.iyer@techcorp.in', 'IT Support', '+91-98765-43216'),
            ('Kavita Joshi', 'kavita.joshi@techcorp.in', 'Operations', '+91-98765-43217'),
            ('Rohit Verma', 'rohit.verma@techcorp.in', 'Product', '+91-98765-43218'),
            ('Deepa Gupta', 'deepa.gupta@techcorp.in', 'Quality Assurance', '+91-98765-43219'),
            ('Arjun Malhotra', 'arjun.malhotra@techcorp.in', 'Business Development', '+91-98765-43220'),
            ('Swati Deshmukh', 'swati.deshmukh@techcorp.in', 'Customer Support', '+91-98765-43221')
        ]
        
        conn.executemany(
            'INSERT INTO employees (name, email, department, phone) VALUES (?, ?, ?, ?)',
            sample_employees
        )
        
        conn.commit()
        conn.close()

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
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
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
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
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

@app.route('/search_contacts', methods=['POST'])
def search_contacts():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    search_term = request.form.get('search_term', '').lower()
    conn = get_db_connection()
    
    if search_term:
        employees = conn.execute(
            'SELECT * FROM employees WHERE LOWER(name) LIKE ? OR LOWER(department) LIKE ?',
            (f'%{search_term}%', f'%{search_term}%')
        ).fetchall()
    else:
        employees = conn.execute('SELECT * FROM employees').fetchall()
    
    conn.close()
    
    results = []
    for emp in employees:
        results.append({
            'name': emp['name'],
            'email': emp['email'],
            'department': emp['department'],
            'phone': emp['phone']
        })
    
    return jsonify(results)

@app.route('/assistant')
def assistant():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('assistant.html')

@app.route('/ask_assistant', methods=['POST'])
def ask_assistant():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    question = request.form.get('question', '').lower()
    
    knowledge_base = {
        'holiday': 'Company holidays include Republic Day (26 Jan), Independence Day (15 Aug), Gandhi Jayanti (2 Oct), Diwali, Holi, Eid, Christmas, and other regional festivals. Please check the HR portal for specific dates.',
        'leave': 'To request leave, submit a request through the HR portal at least 2 weeks in advance. Emergency leave should be reported to your manager and HR immediately via phone call.',
        'benefits': 'Company benefits include comprehensive health insurance (MediClaim), dental coverage, EPF, ESIC, gratuity, and paid time off. Annual health checkup provided. Visit the HR portal or email hr@techcorp.in for details.',
        'it support': 'For IT support, email it-support@techcorp.in or call ext. 5557. For urgent issues, contact the IT helpdesk on the 2nd floor. Working hours: 9 AM to 6 PM IST.',
        'expense': 'Submit expense reports through the finance portal within 7 days of travel/purchase. All receipts must be uploaded with GST details. Manager approval required within 48 hours.',
        'payroll': 'Salary is credited on the last working day of each month. TDS deductions apply. For salary queries, email payroll@techcorp.in or contact ext. 5555.',
        'training': 'Professional development opportunities are available through our learning portal. Annual training budget of ₹50,000 per employee. Certifications and conferences approved by manager.',
        'meeting rooms': 'Book meeting rooms through the Outlook calendar system or facilities portal. Conference rooms available: A1-A4 (4-6 persons), B1-B2 (10-15 persons), C1 (20+ persons). 24-hour advance notice required.',
        'security': 'For security concerns, contact security@techcorp.in or call the emergency line at ext. 9111. Biometric attendance mandatory. Visitor passes required at reception. CCTV monitoring active.',
        'remote work': 'Hybrid work model available. 3 days office, 2 days WFH for eligible positions. Manager approval required. Company laptop provided for WFH. VPN access mandatory.',
        'supplies': 'Office supplies can be ordered through the facilities portal or by contacting facilities@techcorp.in. Stationery available from admin desk on the 1st floor. Print cards with ₹500 monthly credit.',
        'food': 'Cafeteria on ground floor serves breakfast (8:30-10:30 AM) and lunch (12:30-2:30 PM). ₹200 per day meal allowance. Tea/coffee stations available on all floors.',
        'transport': 'Company bus service available from major metro stations. Pickup timing: 8:30 AM. Drop timing: 6:30 PM. Monthly transport pass: ₹2,000. Cab facility for late working (after 8 PM).',
        'pf': 'Provident Fund (PF) contribution: 12% of basic salary by employee + 12% by employer. UAN activation mandatory. Withdrawal allowed for specific reasons as per EPF rules.',
        'medical': 'Annual health checkup provided at empaneled hospitals. Health insurance covers family (spouse + 2 children). ₹5 lakh coverage per person. Mediclaim card provided.',
    }
    
    response = 'I\'m sorry, I don\'t have information about that topic. Please contact HR or your manager for assistance.'
    
    for keyword, answer in knowledge_base.items():
        if keyword in question:
            response = answer
            break
    
    return jsonify({'response': response})

@app.route('/status_formatter')
def status_formatter():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('status_formatter.html')

@app.route('/format_status', methods=['POST'])
def format_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    rough_text = request.form.get('rough_text', '')
    
    cleaned_text = re.sub(r'\s+', ' ', rough_text.strip())
    
    sentences = re.split(r'[.!?]+', cleaned_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) == 0:
        formatted_status = "No content to format."
    elif len(sentences) == 1:
        formatted_status = f"• {sentences[0].capitalize()}."
    else:
        bullet_points = []
        for sentence in sentences[:5]:
            if sentence:
                bullet_points.append(f"• {sentence.capitalize()}.")
        
        if len(sentences) > 5:
            bullet_points.append(f"• Additional points covered in detailed discussion.")
        
        formatted_status = '\n'.join(bullet_points)
    
    formatted_status = f"Daily Status Update - {session['username']}\n\n{formatted_status}\n\nNext Steps:\n• Continuing with current priorities\n• Addressing any blockers as needed"
    
    return jsonify({'formatted_status': formatted_status})

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
```

## **templates/login.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iColleague - Login</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <div class="login-container">
            <div class="logo">
                <h1>iColleague</h1>
                <p>Employee Assistant Platform</p>
            </div>
            
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">{{ message }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            
            <form method="POST" action="{{ url_for('login') }}">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
            
            <p class="register-link">
                Don't have an account? <a href="{{ url_for('register') }}">Register here</a>
            </p>
        </div>
    </div>
</body>
</html>
```

## **templates/dashboard.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iColleague - Dashboard</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <h1>iColleague</h1>
            </div>
            <div class="nav-menu">
                <a href="{{ url_for('dashboard') }}" class="nav-link active">Dashboard</a>
                <a href="{{ url_for('contacts') }}" class="nav-link">Contacts</a>
                <a href="{{ url_for('assistant') }}" class="nav-link">Assistant</a>
                <a href="{{ url_for('status_formatter') }}" class="nav-link">Status Formatter</a>
                <a href="{{ url_for('logout') }}" class="nav-link">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="dashboard">
            <div class="welcome-section">
                <h2>Welcome back, {{ username }}!</h2>
                <p>Your virtual employee assistant is ready to help you.</p>
            </div>

            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">👥</div>
                    <h3>Internal Contacts</h3>
                    <p>Search for employee contact information</p>
                    <a href="{{ url_for('contacts') }}" class="btn btn-secondary">Search Contacts</a>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <h3>Company Assistant</h3>
                    <p>Ask questions about policies & benefits</p>
                    <a href="{{ url_for('assistant') }}" class="btn btn-secondary">Ask Assistant</a>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">📝</div>
                    <h3>Status Formatter</h3>
                    <p>Format your daily status updates</p>
                    <a href="{{ url_for('status_formatter') }}" class="btn btn-secondary">Format Status</a>
                </div>
            </div>

            <div class="quick-stats">
                <h3>Quick Information</h3>
                <div class="stats-grid">
                    <div class="stat-item">
                        <h4>IT Support</h4>
                        <p>ext. 5557</p>
                    </div>
                    <div class="stat-item">
                        <h4>HR</h4>
                        <p>hr@techcorp.in</p>
                    </div>
                    <div class="stat-item">
                        <h4>Emergency</h4>
                        <p>Security: ext. 9111</p>
                    </div>
                    <div class="stat-item">
                        <h4>Cafeteria</h4>
                        <p>Ground Floor</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

## **templates/contacts.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iColleague - Contact Search</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <h1>iColleague</h1>
            </div>
            <div class="nav-menu">
                <a href="{{ url_for('dashboard') }}" class="nav-link">Dashboard</a>
                <a href="{{ url_for('contacts') }}" class="nav-link active">Contacts</a>
                <a href="{{ url_for('assistant') }}" class="nav-link">Assistant</a>
                <a href="{{ url_for('status_formatter') }}" class="nav-link">Status Formatter</a>
                <a href="{{ url_for('logout') }}" class="nav-link">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="page-header">
            <h2>Internal Contact Search</h2>
            <p>Find employee contact information quickly</p>
        </div>

        <div class="search-container">
            <div class="search-form">
                <input type="text" id="searchInput" placeholder="Search by name or department...">
                <button onclick="searchContacts()" class="btn btn-primary">Search</button>
                <button onclick="clearSearch()" class="btn btn-secondary">Clear</button>
            </div>
        </div>

        <div class="results-container">
            <div id="searchResults" class="contact-list">
                <p class="no-results">Enter a search term to find contacts</p>
            </div>
        </div>
    </div>

    <script>
        function searchContacts() {
            const searchTerm = document.getElementById('searchInput').value;
            const resultsDiv = document.getElementById('searchResults');
            
            resultsDiv.innerHTML = '<div class="loading">Searching...</div>';
            
            fetch('/search_contacts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'search_term=' + encodeURIComponent(searchTerm)
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                resultsDiv.innerHTML = '<p class="error">Error searching contacts</p>';
            });
        }

        function displayResults(contacts) {
            const resultsDiv = document.getElementById('searchResults');
            
            if (contacts.length === 0) {
                resultsDiv.innerHTML = '<p class="no-results">No contacts found</p>';
                return;
            }
            
            let html = '<div class="contact-grid">';
            contacts.forEach(contact => {
                html += `
                    <div class="contact-card">
                        <div class="contact-name">${contact.name}</div>
                        <div class="contact-detail">
                            <span class="label">Email:</span>
                            <a href="mailto:${contact.email}">${contact.email}</a>
                        </div>
                        <div class="contact-detail">
                            <span class="label">Department:</span>
                            ${contact.department}
                        </div>
                        <div class="contact-detail">
                            <span class="label">Phone:</span>
                            ${contact.phone}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            
            resultsDiv.innerHTML = html;
        }

        function clearSearch() {
            document.getElementById('searchInput').value = '';
            document.getElementById('searchResults').innerHTML = '<p class="no-results">Enter a search term to find contacts</p>';
        }

        document.getElementById('searchInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchContacts();
            }
        });

        window.onload = function() {
            searchContacts();
        };
    </script>
</body>
</html>
```

## **templates/assistant.html**
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>iColleague - Company Assistant</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-logo">
                <h1>iColleague</h1>
            </div>
            <div class="nav-menu">
                <a href="{{ url_for('dashboard') }}" class="nav-link">Dashboard</a>
                <a href="{{ url_for('contacts') }}" class="nav-link">Contacts</a>
                <a href="{{ url_for('assistant') }}" class="nav-link active">Assistant</a>
                <a href="{{ url_for('status_formatter') }}" class="nav-link">Status Formatter</a>
                <a href="{{ url_for('logout') }}" class="nav-link">Logout</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="page-header">
            <h2>Company Information Assistant</h2>
            <p>Ask questions about Indian company policies, benefits, and procedures</p>
        </div>

        <div class="assistant-container">
            <div class="chat-interface">
                <div class="chat-messages" id="chatMessages">
                    <div class="message bot-message">
                        <div class="message-content">
                            <p>Hello! I'm here to help you with company information. You can ask me about:</p>
                            <ul>
                                <li>Indian holidays and festivals</li>
                                <li>Benefits and salary structure</li>
                                <li>IT support and facilities</li>
                                <li>Meeting rooms and supplies</li>
                                <li>Training and work policies</li>
                                <li>PF, medical, and transportation</li>
                                <li>And much more!</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="chat-input">
                    <input type="text" id="questionInput" placeholder="Ask about company policies..." 
                           onkeypress="handleKeyPress(event)">
                    <button onclick="askQuestion()" class="btn btn-primary">Ask</button>
                </div>
            </div>

            <div class="quick-questions">
                <h3>Quick Questions</h3>
                <div class="question-buttons">
                    <button onclick="quickAsk('How do I request leave?')" class="btn btn-outline">Request Leave</button>
                    <button onclick="quickAsk('What Indian holidays are there?')" class="btn btn-outline">Indian Holidays</button>
                    <button onclick="quickAsk('How do I contact IT support?')" class="btn btn-outline">IT Support</button>
                    <button onclick="quickAsk('What benefits are available?')" class="btn btn-outline">Benefits</button>
                    <button onclick="quickAsk('How do I submit expenses?')" class="btn btn-outline">Expense Reports</button>
                    <button onclick="quickAsk('Tell me about PF and medical?')" class="btn btn-outline">PF & Medical</button>
                    <button onclick="quickAsk('What about transport and food?')" class="btn btn-outline">Transport & Food</button>
                    <button onclick="quickAsk('How do I book meeting rooms?')" class="btn btn-outline">Meeting Rooms</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        function askQuestion() {
            const input = document.getElementById('questionInput');
            const question = input.value.trim();
            
            if (!question) return;
            
            addMessage(question, 'user');
            input.value = '';
            
            const messagesDiv = document.getElementById('chatMessages');
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'message bot-message typing





