# iColleague - Virtual Employee Assistant

A full-stack web application built with Flask that provides employees with a virtual assistant for company-related tasks and information.

## Features

### 1. User Authentication
- Simple username/password login system
- User registration
- Session-based authentication
- Secure password hashing

### 2. Dashboard
- Personalized welcome message
- Quick navigation to all features
- Important contact information at a glance

### 3. Internal Contact Search
- Search employees by name or department
- Displays email, department, and phone information
- Pre-populated with sample employee data
- Real-time search functionality

### 4. Company Information Assistant
- Interactive chat interface
- Keyword-based responses for common questions
- Quick question buttons for common topics
- Topics include: Indian holidays, festivals, leave, benefits, IT support, expenses, payroll, training, meeting rooms, security, remote work, PF, medical, transport, food

### 5. Daily Status Formatter
- Transform rough notes into professional status updates
- Bullet point formatting
- Copy to clipboard functionality
- Download formatted status as text file
- Example inputs provided

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: SQLite
- **Authentication**: Werkzeug password hashing
- **Deployment**: Ready for Render.com with Gunicorn

## Project Structure

```
iColleague/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── Procfile                 # Render.com deployment configuration
├── runtime.txt              # Python version specification
├── templates/               # HTML templates
│   ├── login.html          # Login page
│   ├── register.html        # Registration page
│   ├── dashboard.html      # Main dashboard
│   ├── contacts.html       # Contact search interface
│   ├── assistant.html      # Process assistant chat
│   └── status_formatter.html # Status formatting tool
├── static/                 # Static assets
│   └── css/
│       └── style.css       # Application styles
└── instance/               # Database storage (auto-created)
    └── icolleague.db       # SQLite database
```

## Installation & Running Locally

1. **Navigate to the project directory:**
   ```bash
   cd "C:\Users\thilak\OneDrive\Desktop\sudhakar\iColleague"
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   Open your browser and go to `http://localhost:5000`

## Deployment on Render.com

The application is pre-configured for deployment on Render.com:

1. Create a new account on Render.com
2. Create a new Web Service
3. Connect your GitHub repository or upload the files
4. Render will automatically detect the Python web service
5. The application will be built and deployed using:
   - `gunicorn app:app` (specified in Procfile)
   - Python 3.9.16 (specified in runtime.txt)

## Database

The application uses SQLite with auto-initialization:
- Creates database on first run
- Automatically populates with sample employee data
- Two main tables: `users` and `employees`

## Sample Employees

The database comes pre-populated with 12 Indian employees across different departments:
- Engineering: Rajesh Kumar, Vikram Singh
- Human Resources: Priya Sharma
- Marketing: Amit Patel
- Finance: Anjali Reddy
- Sales: Meera Nair
- IT Support: Suresh Iyer
- Operations: Kavita Joshi
- Product: Rohit Verma
- Quality Assurance: Deepa Gupta
- Business Development: Arjun Malhotra
- Customer Support: Swati Deshmukh

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Input validation and sanitization
- Protection against SQL injection (parameterized queries)

## Usage

1. **First Time**: Register a new user account
2. **Login**: Use your credentials to access the dashboard
3. **Explore Features**: Use the navigation menu to access all tools
4. **Search Contacts**: Find colleague information quickly
5. **Ask Assistant**: Get answers to company policy questions
6. **Format Status**: Create professional daily status updates

## Indian Company Details Included

The application now includes:
- Indian employee names and contact details
- Indian phone numbers (+91 format)
- Indian company email domains (.in)
- Indian holidays (Republic Day, Independence Day, Diwali, Holi, Eid, etc.)
- Indian benefits structure (PF, ESIC, MediClaim, gratuity)
- Indian salary structure and taxation information
- Indian office timings (9 AM - 6 PM IST)
- Indian transportation and food facilities
- Regional festival considerations

## Customization

- Update the `knowledge_base` dictionary in `app.py` to add more Indian-specific Q&A responses
- Modify the sample employee data during database initialization
- Customize the CSS in `static/css/style.css` for different branding
- Add new features by creating additional Flask routes and templates

## Support

This application uses only free and open-source dependencies. No external paid services are required for operation.