# 🎓 Student Management System

A simple and user-friendly **Student Management System** built using Python and Flask. This web application helps manage student details through a clean web interface.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.3-black?logo=flask)
![Testing](https://img.shields.io/badge/Tests-pytest-green?logo=pytest)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📌 Project Overview

The Student Management System is a web-based application developed using Flask. It provides basic student record management functionality through a browser.

The application currently supports:
- Viewing the student list.
- Adding new student records.
- Deleting student records.
- Validating required student details.

## ✨ Features

- **Student Management:** Add and view student information.
- **Delete Records:** Remove student records from the list.
- **Input Validation:** Checks that name, roll number and course are provided.
- **Web Interface:** Uses Flask templates to render the application.
- **Automated Testing:** Includes pytest tests for important application routes.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Web application framework |
| HTML | Web page structure |
| CSS | User interface styling |
| pytest | Automated testing |
| Gunicorn | WSGI server dependency |

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
│   └── index.html
│
├── app.py
├── test_app.py
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

## ▶️ Run the Application

Start the Flask application:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## 🧪 Run Automated Tests

Run the following command:

```bash
python -m pytest -v
```

The test suite checks:
- Home page response.
- Adding a student.
- Deleting a student.
- Handling missing student details.

## 🔄 Continuous Integration

This project uses GitHub Actions to automate testing.

Whenever code is pushed to the `main` branch or a pull request is created, GitHub Actions can install the dependencies and run the pytest suite automatically.

View the workflow results in the **Actions** tab of this repository.

## ⚠️ Current Project Limitations

- Student records are currently stored in memory and are not permanently saved.
- Records are reset when the application restarts.
- Authentication and role-based access are not currently implemented.
- This project is intended as a learning project, not a production student-record system.

## 🚀 Future Improvements

- Add database integration using SQLite or MySQL.
- Implement student update functionality.
- Add user authentication and authorization.
- Add search and filtering.
- Improve input validation.
- Add student profile management.
- Introduce pagination for larger student lists.

## 👩‍💻 Author

**ljnanashree**

GitHub: [@ljnanashree](https://github.com/ljnanashree)

## 📄 License

This project is currently published without a specified license. Add a LICENSE file if you want to distribute it under an open-source license.

---

⭐ If you find this project useful, consider giving the repository a star!