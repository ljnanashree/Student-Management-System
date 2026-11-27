# 🎓 Student Management System

A complete, user-friendly **Student Management System** built using Python and Flask. This web application provides student record management, attendance tracking, reports, analytics, activity monitoring, and CSV exports through a modern dashboard interface.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.3-black?logo=flask)
![Tests](https://img.shields.io/badge/Tests-62%20Passed-brightgreen?logo=pytest)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI-green?logo=githubactions)
![Deployment](https://img.shields.io/badge/Deployment-Render-purple?logo=render)

---

## 📌 Project Overview

The **Student Management System** is a web-based application developed using Python and Flask to simplify student record management and attendance tracking.

It provides an administrator dashboard to manage student information, record daily attendance, monitor attendance percentages, generate analytical reports, and export records as CSV files.

The system supports manual and bulk attendance marking, date-based filtering, automated testing, and database management using SQLite and PostgreSQL.

## ✨ Features

### 👨‍🎓 Student Management
- Add new student records.
- View all registered students.
- Edit existing student information.
- Delete student records.
- Search students by relevant details.
- Validate required student information.
- Prevent duplicate roll numbers.

### 🔐 Authentication and Security
- Administrator login system.
- Password-based authentication.
- Protected application routes.
- Secure logout functionality.
- Password hashing.
- Activity logging to track important administrative actions.

### 📅 Attendance Management
- View the attendance management dashboard.
- Mark students as Present or Absent manually.
- Perform bulk attendance marking.
- Correct attendance records after bulk marking.
- Prevent duplicate attendance records for the same student and date.
- View attendance history by selecting a date.
- Validate attendance dates.
- Track individual student attendance.

### 📊 Reports and Analytics
- Interactive reports and analytics dashboard.
- Daily attendance trend visualization.
- Present vs Absent doughnut chart.
- Course-wise student distribution chart.
- Student-wise attendance percentage chart.
- Calculate individual student attendance percentages.
- Filter reports by date range.
- View attendance history.
- Display total attendance, present and absent records.
- Monitor course distribution.

### 🚨 Dashboard Notifications
- Low Attendance Alerts for students below 75%.
- Attendance Missing notifications for students without attendance records.
- Recent Activities notification showing the latest recorded activities.
- Separate identification of students with no attendance records.

### 📈 Attendance Visualization
- Color-coded attendance status badges.
- Low attendance indicators.
- Good attendance indicators.
- Not Recorded status for students without attendance records.
- Visual attendance progress bars.

### 📝 Activity Monitoring
- Track student additions.
- Track student updates.
- Track student deletions.
- Record manual attendance activities.
- Record bulk attendance activities.
- Display the latest 10 activities in the Reports dashboard.

### 📥 CSV Export
- Export student records as CSV.
- Export attendance records as CSV.
- Download attendance for a selected date.
- Organize exported information for further analysis.

### 🧪 Automated Testing
- Pytest-based automated test suite.
- Tests student management functionality.
- Tests authentication and protected routes.
- Tests manual and bulk attendance.
- Tests attendance history and analytics.
- Tests CSV exports.
- Tests activity logging and reporting.

**Latest confirmed test result: 62 tests passed.**

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.11+ | Core programming language |
| Flask | Web application framework |
| SQLite | Test database |
| PostgreSQL | Production database |
| HTML5 | Web page structure |
| CSS3 | Dashboard styling |
| JavaScript | Interactive functionality |
| Chart.js | Data visualization |
| Jinja2 | Dynamic HTML templates |
| pytest | Automated testing |
| Gunicorn | Production WSGI server |
| Git & GitHub | Version control |
| GitHub Actions | Continuous integration |
| Render | Cloud deployment |

## 📁 Project Structure

```text
Student-Management-System/
│
├── .github/
│   └── workflows/
│       └── python-tests.yml
│
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── edit.html
│   ├── reports.html
│   └── attendance.html
│
├── app.py
├── test_app.py
├── migrate_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/ljnanashree/Student-Management-System.git
```

### 2. Open the project folder

```bash
cd Student-Management-System
```

### 3. Create a virtual environment

Windows:

```powershell
py -m venv venv
```

### 4. Activate the virtual environment

```powershell
venv\Scripts\activate
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Configure environment variables

Configure the environment variables required by your application, including:

- `SECRET_KEY`
- `DATABASE_URL`

Use the appropriate database configuration for your environment.

**Important:** Never commit passwords, secret keys, or database credentials to GitHub.

## ▶️ Run the Application

Start the Flask application:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

Log in using your configured administrator credentials.

## 🧪 Run Automated Tests

Run the following command:

```bash
python -m pytest -v
```

**Latest confirmed result: 62 tests passed.**

The test suite covers:

- Login and authentication.
- Protected routes.
- Student addition, editing, and deletion.
- Duplicate roll number prevention.
- Student search.
- Reports and analytics.
- Student CSV export.
- Manual attendance.
- Bulk attendance.
- Attendance correction.
- Duplicate attendance prevention.
- Attendance history.
- Invalid attendance date handling.
- Attendance analytics.
- Attendance CSV export.
- Activity logging.

## 🔄 Continuous Integration – GitHub Actions

This project uses GitHub Actions to automate testing.

Whenever code is pushed to the `main` branch or a pull request is created, the configured workflow installs dependencies and executes the automated test suite.

View the workflow results:

[GitHub Actions – Student Management System](https://github.com/ljnanashree/Student-Management-System/actions)

## 🚀 Live Deployment

The application is deployed using **Render**.

- Hosting platform: Render
- Source code: GitHub
- Database: PostgreSQL
- Continuous integration: GitHub Actions
- Production server: Gunicorn

**Live Application:** https://student-management-system-j6en.onrender.com

## 🔮 Future Improvements

- Role-based access for administrators, teachers, and students.
- Student profile photographs and document uploads.
- PDF report generation.
- Email notifications for low attendance.
- Advanced dashboard customization.
- Advanced filtering and pagination.
- More detailed student performance analytics.
- Improved reporting and data visualization.

## 👩‍💻 Author

**ljnanashree**

GitHub: [@ljnanashree](https://github.com/ljnanashree)

Repository: [Student Management System](https://github.com/ljnanashree/Student-Management-System)

## 📄 License

No open-source license has currently been specified.

A LICENSE file can be added if the project is intended for distribution under an open-source license.

---

⭐ If you find this project useful, consider giving the repository a star!