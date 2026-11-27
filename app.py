
import os
import sqlite3
import csv
import io
from datetime import date, datetime
from functools import wraps

import psycopg
from psycopg.rows import dict_row

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, make_response, Response
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
class DatabaseConnection:
    def __init__(self, connection, is_postgres):
        self.connection = connection
        self.is_postgres = is_postgres

    def execute(self, query, params=()):
        if self.is_postgres:
            query = query.replace("?", "%s")

        return self.connection.execute(query, params)

    def __enter__(self):
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.connection.__exit__(
            exc_type, exc_value, traceback
        )



def get_db():
    # SQLite is allowed only during automated tests.
    if app.config.get("TESTING"):
        connection = sqlite3.connect(app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        return DatabaseConnection(connection, False)

    # Production must always use PostgreSQL.
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. PostgreSQL connection required."
        )

    connection = psycopg.connect(
        database_url,
        row_factory=dict_row
    )

    return DatabaseConnection(connection, True)



# CREATE TABLES AND INITIAL ADMIN
def init_db():
    is_postgres = (
        bool(os.environ.get("DATABASE_URL"))
        and not app.config.get("TESTING")
    )

    if is_postgres:
        students_table = """
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                roll TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL
            )
        """

        admins_table = """
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """

        attendance_table = """
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                student_id INTEGER NOT NULL
                    REFERENCES students(id) ON DELETE CASCADE,
                attendance_date DATE NOT NULL,
                status TEXT NOT NULL
                    CHECK (status IN ('Present', 'Absent')),
                UNIQUE (student_id, attendance_date)
            )
        """

    else:
        students_table = """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL
            )
        """

        admins_table = """
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """

        attendance_table = """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL
                    REFERENCES students(id) ON DELETE CASCADE,
                attendance_date DATE NOT NULL,
                status TEXT NOT NULL
                    CHECK (status IN ('Present', 'Absent')),
                UNIQUE (student_id, attendance_date)
            )
        """

    with get_db() as db:
        db.execute(students_table)
        db.execute(admins_table)
        db.execute(attendance_table)


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
    "SELECT COUNT(*) AS count FROM students"
).fetchone()["count"]

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

    except (sqlite3.IntegrityError, psycopg.IntegrityError):
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
            "SELECT COUNT(*) AS count FROM students"
        ).fetchone()["count"]

        # Total courses
        course_count = db.execute(
            "SELECT COUNT(DISTINCT course) AS count FROM students"
        ).fetchone()["count"]

        # Course distribution
        course_stats = db.execute("""
            SELECT course, COUNT(*) AS student_count
            FROM students
            GROUP BY course
            ORDER BY student_count DESC
        """).fetchall()

        # Recently added students
        recent_students = db.execute("""
            SELECT * FROM students
            ORDER BY id DESC
            LIMIT 5
        """).fetchall()

        # Overall attendance summary
        attendance_summary = db.execute("""
            SELECT
                COUNT(*) AS total_records,
                COALESCE(SUM(
                    CASE WHEN status = 'Present' THEN 1 ELSE 0 END
                ), 0) AS present_count,
                COALESCE(SUM(
                    CASE WHEN status = 'Absent' THEN 1 ELSE 0 END
                ), 0) AS absent_count
            FROM attendance
        """).fetchone()

        # Individual student attendance
        student_attendance = db.execute("""
            SELECT
                s.id,
                s.name,
                s.roll,
                s.course,
                COUNT(a.id) AS total_days,
                COALESCE(SUM(
                    CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END
                ), 0) AS present_days
            FROM students s
            LEFT JOIN attendance a
                ON s.id = a.student_id
            GROUP BY s.id, s.name, s.roll, s.course
            ORDER BY s.name ASC
        """).fetchall()

        # Attendance history - latest 10 dates
        attendance_history = db.execute("""
            SELECT
                attendance_date,
                COUNT(*) AS total_students,
                COALESCE(SUM(
                    CASE WHEN status = 'Present' THEN 1 ELSE 0 END
                ), 0) AS present_count,
                COALESCE(SUM(
                    CASE WHEN status = 'Absent' THEN 1 ELSE 0 END
                ), 0) AS absent_count
            FROM attendance
            GROUP BY attendance_date
            ORDER BY attendance_date DESC
            LIMIT 10
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

    # Overall attendance calculations
    attendance_total = attendance_summary["total_records"]
    attendance_present = attendance_summary["present_count"]
    attendance_absent = attendance_summary["absent_count"]

    attendance_rate = (
        round(attendance_present / attendance_total * 100, 1)
        if attendance_total else 0
    )

    # Individual student percentages
    attendance_data = []

    for student in student_attendance:
        total_days = student["total_days"]
        present_days = student["present_days"]

        percentage = (
            round(present_days / total_days * 100, 1)
            if total_days else 0
        )

        attendance_data.append({
            "name": student["name"],
            "roll": student["roll"],
            "course": student["course"],
            "total_days": total_days,
            "present_days": present_days,
            "percentage": percentage
        })

    return render_template(
        "reports.html",
        total=total,
        course_count=course_count,
        course_stats=course_data,
        recent_students=recent_students,
        attendance_total=attendance_total,
        attendance_present=attendance_present,
        attendance_absent=attendance_absent,
        attendance_rate=attendance_rate,
        attendance_data=attendance_data,
        attendance_history=attendance_history
    )


# ATTENDANCE MANAGEMENT

def get_valid_attendance_date(value):
    """Validate attendance date and return YYYY-MM-DD."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date().isoformat()
    except (ValueError, TypeError):
        return None


# VIEW ATTENDANCE
@app.route("/attendance")
@login_required
def attendance():
    selected_date = get_valid_attendance_date(
        request.args.get("date", date.today().isoformat())
    )

    if not selected_date:
        return "Invalid attendance date", 400

    with get_db() as db:
        students = db.execute("""
            SELECT
                s.id,
                s.name,
                s.roll,
                s.course,
                COALESCE(a.status, 'Absent') AS status
            FROM students s
            LEFT JOIN attendance a
                ON s.id = a.student_id
                AND a.attendance_date = ?
            ORDER BY s.id ASC
        """, (selected_date,)).fetchall()

    return render_template(
        "attendance.html",
        students=students,
        selected_date=selected_date
    )


# SAVE MANUAL ATTENDANCE
@app.route("/attendance/save", methods=["POST"])
@login_required
def save_attendance():
    selected_date = get_valid_attendance_date(
        request.form.get("date")
    )

    if not selected_date:
        return "Invalid attendance date", 400

    with get_db() as db:

        students = db.execute(
            "SELECT id FROM students"
        ).fetchall()

        for student in students:
            student_id = student["id"]

            status = request.form.get(
                f"status_{student_id}"
            )

            if status not in ("Present", "Absent"):
                return "Invalid attendance status", 400

            db.execute("""
                INSERT INTO attendance
                    (student_id, attendance_date, status)
                VALUES (?, ?, ?)
                ON CONFLICT (student_id, attendance_date)
                DO UPDATE SET status = excluded.status
            """, (student_id, selected_date, status))

    return redirect(url_for(
        "attendance",
        date=selected_date
    ))


# BULK AUTOMATIC ATTENDANCE
@app.route("/attendance/bulk", methods=["POST"])
@login_required
def bulk_attendance():
    selected_date = get_valid_attendance_date(
        request.form.get("date")
    )

    if not selected_date:
        return "Invalid attendance date", 400

    with get_db() as db:

        students = db.execute(
            "SELECT id FROM students"
        ).fetchall()

        for student in students:
            db.execute("""
                INSERT INTO attendance
                    (student_id, attendance_date, status)
                VALUES (?, ?, 'Present')
                ON CONFLICT (student_id, attendance_date)
                DO UPDATE SET status = 'Present'
            """, (student["id"], selected_date))

    return redirect(url_for(
        "attendance",
        date=selected_date
    ))


# EXPORT ATTENDANCE TO CSV
@app.route("/attendance/export")
@login_required
def export_attendance_csv():
    selected_date = request.args.get(
        "date", date.today().isoformat()
    )

    valid_date = get_valid_attendance_date(selected_date)

    if not valid_date:
        return "Invalid attendance date", 400

    with get_db() as db:
        records = db.execute("""
            SELECT
                a.attendance_date,
                s.roll,
                s.name,
                s.course,
                a.status
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.attendance_date = ?
            ORDER BY s.roll ASC
        """, (valid_date,)).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Attendance Date",
        "Roll Number",
        "Student Name",
        "Course",
        "Status"
    ])

    for record in records:
        writer.writerow([
            record["attendance_date"],
            record["roll"],
            record["name"],
            record["course"],
            record["status"]
        ])

    filename = f"attendance_{valid_date}.csv"

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                f"attachment; filename={filename}"
        }
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
