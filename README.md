# 🎓 Student Management System

A complete, user-friendly **Student Management System** built using Python and Flask. This web application provides student record management, attendance tracking, reports, analytics and CSV exports through a clean web interface.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.3-black?logo=flask)
![Testing](https://img.shields.io/badge/Tests-31%20Passed-brightgreen?logo=pytest)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Passing-green?logo=githubactions)
![Deployment](https://img.shields.io/badge/Deployment-Render-purple?logo=render)

---

## 📌 Project Overview

The **Student Management System** is a web-based application developed using Python and Flask to simplify student record management and attendance tracking.

It provides an admin interface to manage student information, record daily attendance, monitor attendance percentages, generate reports and export data as CSV files.

The application supports both manual and bulk attendance marking, making attendance management easier and more efficient.

## ✨ Features

### 👨‍🎓 Student Management
- Add new student records.
- View all registered students.
- Edit existing student information.
- Delete student records.
- Search students by relevant details.
- Validate required student information.
- Prevent duplicate roll numbers.

### 🔐 Authentication
- Admin login system.
- Password-based authentication.
- Protected application routes.
- Secure logout functionality.

### 📅 Attendance Management
- View the attendance management dashboard.
- Mark students as Present or Absent manually.
- Automatically mark all students Present using bulk attendance.
- Correct attendance records after bulk marking.
- Prevent duplicate attendance records for the same student and date.
- View attendance history by selecting a date.
- Validate attendance dates.

### 📊 Reports and Analytics
- Student reports and course distribution.
- Attendance analytics dashboard.
- Calculate individual student attendance percentages.
- View attendance history.
- Track Present and Absent records.
- Display attendance information for reporting.

### 📥 CSV Export
- Export student records as CSV.
- Export attendance records as CSV.
- Download attendance for a selected date.
- Organize exported information for further analysis.

### ⚙️ Automated Testing
- Includes a pytest-based automated test suite.
- Tests student management functionality.
- Tests authentication and protected routes.
- Tests manual and bulk attendance.
- Tests attendance history and analytics.
- Tests CSV exports.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Web application framework |
| SQLite / PostgreSQL | Database management |
| HTML | Web page structure |
| CSS | User interface styling |
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
│   └── CSS and other static assets
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

Configure the required environment variables for your application, including the secret key and database connection settings.

Do not commit passwords, secret keys or database credentials to GitHub.

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

**Latest testing result: 31 tests passed.**

The test suite covers:

- Login and authentication.
- Student addition, editing and deletion.
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
- Protected routes.

## 🔄 Continuous Integration – GitHub Actions

This project uses GitHub Actions to automate testing.

Whenever code is pushed to the `main` branch or a pull request is created, the configured workflow installs dependencies and executes the automated test suite.

View the workflow results:

[GitHub Actions – Student Management System](https://github.com/ljnanashree/Student-Management-System/actions)

## 🚀 Live Deployment

The application is deployed using **Render**.

- Hosting platform: Render
- Source code: GitHub
- Continuous integration: GitHub Actions
- Deployment status: Live

**Live Application:** Add your Render website URL here.

## 🔮 Future Improvements

- Role-based access for administrators, teachers and students.
- Student profile photographs and document uploads.
- Advanced attendance reports and visual charts.
- Email notifications for attendance.
- PDF report generation.
- Improved dashboard customization.
- Advanced filtering and pagination.

## 👩‍💻 Author

**ljnanashree**

GitHub: [@ljnanashree](https://github.com/ljnanashree)

Repository: [Student Management System](https://github.com/ljnanashree/Student-Management-System)

## 📄 License

No open-source license has currently been specified.

A LICENSE file can be added if the project is intended for distribution under an open-source license.

---

⭐ If you find this project useful, consider giving the repository a star!