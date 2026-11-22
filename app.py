
import os
import sqlite3
import csv
import io
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, make_response
)

from werkzeug.security import (
    generate_password_hash, check_password_hash
)

app = Flask(__name__)

# Use an environment variable for the secret key.
# The fallback is for local development only.
app.secret_key = os.environ.get(
    "SECRET_KEY", "development-only-change-this-secret"
)

app.config["DATABASE"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "students.db"
)


# DATABASE CONNECTION
def get_db():
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db


# CREATE TABLES AND INITIAL ADMIN
def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)

        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD", "Admin@123")

        existing_admin = db.execute(
            "SELECT id FROM admins WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_admin is None:
            db.execute("""
                INSERT INTO admins (username, password_hash)
                VALUES (?, ?)
            """, (username, generate_password_hash(password)))


# LOGIN PROTECTION
def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped_view


# ADMIN LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if "admin" in session:
        return redirect(url_for("home"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db() as db:
            admin = db.execute(
                "SELECT * FROM admins WHERE username = ?",
                (username,)
            ).fetchone()

        if admin and check_password_hash(
            admin["password_hash"], password
        ):
            session.clear()
            session["admin"] = admin["username"]
            return redirect(url_for("home"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


# ADMIN LOGOUT
@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


# HOME PAGE - VIEW AND SEARCH STUDENTS
@app.route("/")
@login_required
def home():
    search = request.args.get("q", "").strip()

    with get_db() as db:
        students = db.execute("""
            SELECT * FROM students
            WHERE name LIKE ? OR roll LIKE ? OR course LIKE ?
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()

        total = db.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

    return render_template(
        "index.html",
        students=students,
        total=total,
        search=search
    )


# ADD STUDENT
@app.route("/add", methods=["POST"])
@login_required
def add_student():
    name = request.form.get("name", "").strip()
    roll = request.form.get("roll", "").strip()
    course = request.form.get("course", "").strip()

    if not name or not roll or not course:
        return "All fields are required", 400

    try:
        with get_db() as db:
            db.execute("""
                INSERT INTO students (name, roll, course)
                VALUES (?, ?, ?)
            """, (name, roll, course))

    except sqlite3.IntegrityError:
        return "Roll number already exists", 409

    return redirect(url_for("home"))


# DELETE STUDENT
@app.route("/delete/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    with get_db() as db:
        db.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

    return redirect(url_for("home"))


# EDIT AND UPDATE STUDENT
@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    with get_db() as db:
        student = db.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

        if student is None:
            return "Student not found", 404

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            roll = request.form.get("roll", "").strip()
            course = request.form.get("course", "").strip()

            if not name or not roll or not course:
                return "All fields are required", 400

            try:
                db.execute("""
                    UPDATE students
                    SET name = ?, roll = ?, course = ?
                    WHERE id = ?
                """, (name, roll, course, student_id))

                return redirect(url_for("home"))

            except sqlite3.IntegrityError:
                return "Roll number already exists", 409

    return render_template("edit.html", student=student)

# REPORTS AND ANALYTICS
@app.route("/reports")
@login_required
def reports():
    with get_db() as db:

        # Total students
        total = db.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        # Number of different courses
        course_count = db.execute(
            "SELECT COUNT(DISTINCT course) FROM students"
        ).fetchone()[0]

        # Students in each course
        course_stats = db.execute("""
            SELECT course, COUNT(*) AS student_count
            FROM students
            GROUP BY course
            ORDER BY student_count DESC
        """).fetchall()

        # Recently added records
        recent_students = db.execute("""
            SELECT * FROM students
            ORDER BY id DESC
            LIMIT 5
        """).fetchall()

    # Calculate course percentages
    course_data = []

    for item in course_stats:
        percentage = (
            round(item["student_count"] / total * 100, 1)
            if total else 0
        )

        course_data.append({
            "course": item["course"],
            "student_count": item["student_count"],
            "percentage": percentage
        })

    return render_template(
        "reports.html",
        total=total,
        course_count=course_count,
        course_stats=course_data,
        recent_students=recent_students
    )


# EXPORT STUDENTS TO CSV
@app.route("/export")
@login_required
def export_students():
    with get_db() as db:
        students = db.execute("""
            SELECT id, name, roll, course
            FROM students
            ORDER BY id DESC
        """).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Student Name", "Roll Number", "Course"])

    for student in students:
        writer.writerow([
            student["id"],
            student["name"],
            student["roll"],
            student["course"]
        ])

    response = make_response(output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        "attachment; filename=student_report.csv"
    )

    return response

# RUN APPLICATION
if __name__ == "__main__":
    init_db()
    app.run(debug=False)
