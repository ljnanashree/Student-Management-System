
import csv
import io
import pytest

from app import app, init_db, get_db


@pytest.fixture
def client(tmp_path):
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["DATABASE"] = str(tmp_path / "test.db")

    init_db()

    with app.test_client() as client:
        yield client


def login(client):
    return client.post("/login", data={
        "username": "admin",
        "password": "Admin@123"
    }, follow_redirects=True)


def add_test_student(client, name="Rahul",
                     roll="101", course="BCA"):
    return client.post("/add", data={
        "name": name,
        "roll": roll,
        "course": course
    })


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_valid_login(client):
    response = login(client)
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_invalid_login(client):
    response = client.post("/login", data={
        "username": "admin",
        "password": "wrong"
    })
    assert b"Invalid username or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location


def test_add_student(client):
    login(client)
    response = add_test_student(client)

    assert response.status_code == 302

    with get_db() as db:
        student = db.execute(
            "SELECT * FROM students WHERE roll = '101'"
        ).fetchone()

    assert student is not None
    assert student["name"] == "Rahul"


def test_duplicate_roll_number(client):
    login(client)
    add_test_student(client)

    response = add_test_student(
        client, "Another Student", "101", "BSc"
    )

    assert response.status_code == 409


def test_edit_student(client):
    login(client)
    add_test_student(client)

    with get_db() as db:
        student = db.execute(
            "SELECT id FROM students WHERE roll = '101'"
        ).fetchone()

    response = client.post(
        f"/edit/{student['id']}",
        data={
            "name": "Rahul Kumar",
            "roll": "101",
            "course": "BCA Computer Science"
        }
    )

    assert response.status_code == 302

    with get_db() as db:
        updated = db.execute(
            "SELECT * FROM students WHERE id = ?",
            (student["id"],)
        ).fetchone()

    assert updated["name"] == "Rahul Kumar"
    assert updated["course"] == "BCA Computer Science"


def test_delete_student(client):
    login(client)
    add_test_student(client)

    with get_db() as db:
        student = db.execute(
            "SELECT id FROM students WHERE roll = '101'"
        ).fetchone()

    response = client.post(
        f"/delete/{student['id']}"
    )

    assert response.status_code == 302

    with get_db() as db:
        deleted = db.execute(
            "SELECT * FROM students WHERE id = ?",
            (student["id"],)
        ).fetchone()

    assert deleted is None


def test_search_student(client):
    login(client)
    add_test_student(client)

    response = client.get("/?q=Rahul")

    assert response.status_code == 200
    assert b"Rahul" in response.data


def test_reports(client):
    login(client)
    add_test_student(client)

    response = client.get("/reports")

    assert response.status_code == 200
    assert b"Course Distribution" in response.data


def test_csv_export(client):
    login(client)
    add_test_student(client)

    response = client.get("/export")

    assert response.status_code == 200
    assert "text/csv" in response.content_type

    rows = list(csv.reader(
        io.StringIO(response.get_data(as_text=True))
    ))

    assert rows[0] == [
        "ID", "Student Name", "Roll Number", "Course"
    ]
    assert rows[1][1:] == ["Rahul", "101", "BCA"]


def test_logout(client):
    login(client)

    response = client.post(
        "/logout",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Welcome Back!" in response.data


def test_reports_require_login(client):
    response = client.get("/reports")

    assert response.status_code == 302
    assert "/login" in response.location


def test_export_requires_login(client):
    response = client.get("/export")

    assert response.status_code == 302
    assert "/login" in response.location


def test_add_requires_login(client):
    response = add_test_student(client)

    assert response.status_code == 302
    assert "/login" in response.location

# ==============================
# ATTENDANCE TESTS
# ==============================

def test_attendance_page(client):
    login(client)
    add_test_student(client)

    response = client.get("/attendance")

    assert response.status_code == 200
    assert b"Attendance Management" in response.data
    assert b"Rahul" in response.data


def test_attendance_requires_login(client):
    response = client.get("/attendance")

    assert response.status_code == 302
    assert "/login" in response.location


def test_manual_attendance(client):
    login(client)
    add_test_student(client)

    with get_db() as db:
        student = db.execute(
            "SELECT id FROM students WHERE roll = '101'"
        ).fetchone()

    response = client.post("/attendance/save", data={
        "date": "2026-11-27",
        f"status_{student['id']}": "Present"
    })

    assert response.status_code == 302

    with get_db() as db:
        record = db.execute(
            "SELECT * FROM attendance WHERE student_id = ?",
            (student["id"],)
        ).fetchone()

    assert record["status"] == "Present"


def test_manual_absent_attendance(client):
    login(client)
    add_test_student(client)

    with get_db() as db:
        student = db.execute(
            "SELECT id FROM students WHERE roll = '101'"
        ).fetchone()

    client.post("/attendance/save", data={
        "date": "2026-11-27",
        f"status_{student['id']}": "Absent"
    })

    with get_db() as db:
        record = db.execute(
            "SELECT status FROM attendance WHERE student_id = ?",
            (student["id"],)
        ).fetchone()

    assert record["status"] == "Absent"


def test_bulk_attendance(client):
    login(client)
    add_test_student(client)
    add_test_student(client, "Priya", "102", "BCA")

    response = client.post("/attendance/bulk", data={
        "date": "2026-11-27"
    })

    assert response.status_code == 302

    with get_db() as db:
        records = db.execute("""
            SELECT status FROM attendance
            WHERE attendance_date = ?
        """, ("2026-11-27",)).fetchall()

    assert len(records) == 2
    assert all(r["status"] == "Present" for r in records)


def test_correct_bulk_attendance(client):
    login(client)
    add_test_student(client)
    add_test_student(client, "Priya", "102", "BCA")

    client.post("/attendance/bulk", data={
        "date": "2026-11-27"
    })

    with get_db() as db:
        student = db.execute(
            "SELECT id FROM students WHERE roll = '102'"
        ).fetchone()

    client.post("/attendance/save", data={
        "date": "2026-11-27",
        "status_1": "Present",
        f"status_{student['id']}": "Absent"
    })

    with get_db() as db:
        record = db.execute(
            "SELECT status FROM attendance WHERE student_id = ?",
            (student["id"],)
        ).fetchone()

    assert record["status"] == "Absent"


def test_duplicate_attendance_prevention(client):
    login(client)
    add_test_student(client)

    with get_db() as db:
        student = db.execute(
            "SELECT id FROM students WHERE roll = '101'"
        ).fetchone()

    attendance_data = {
        "date": "2026-11-27",
        f"status_{student['id']}": "Present"
    }

    client.post("/attendance/save", data=attendance_data)
    client.post("/attendance/save", data=attendance_data)

    with get_db() as db:
        count = db.execute("""
            SELECT COUNT(*) AS count
            FROM attendance
            WHERE student_id = ?
            AND attendance_date = ?
        """, (student["id"], "2026-11-27")).fetchone()["count"]

    assert count == 1


def test_attendance_history(client):
    login(client)
    add_test_student(client)

    with get_db() as db:
        student = db.execute(
            "SELECT id FROM students WHERE roll = '101'"
        ).fetchone()

    client.post("/attendance/save", data={
        "date": "2026-11-26",
        f"status_{student['id']}": "Present"
    })

    response = client.get(
        "/attendance?date=2026-11-26"
    )

    assert response.status_code == 200
    assert b"2026-11-26" in response.data
    assert b"Present" in response.data


def test_invalid_attendance_date(client):
    login(client)

    response = client.get(
        "/attendance?date=invalid"
    )

    assert response.status_code == 400


# ==============================
# ATTENDANCE ANALYTICS TESTS
# ==============================

def test_reports_attendance_analytics(client):
    login(client)
    add_test_student(client)

    with get_db() as db:
        student = db.execute(
            "SELECT id FROM students WHERE roll = '101'"
        ).fetchone()

    client.post("/attendance/save", data={
        "date": "2026-11-27",
        f"status_{student['id']}": "Present"
    })

    response = client.get("/reports")

    assert response.status_code == 200
    assert b"Attendance Analytics" in response.data
    assert b"Student Attendance Percentage" in response.data
    assert b"100.0%" in response.data


def test_reports_attendance_history(client):
    login(client)
    add_test_student(client)

    with get_db() as db:
        student = db.execute(
            "SELECT id FROM students WHERE roll = '101'"
        ).fetchone()

    client.post("/attendance/save", data={
        "date": "2026-11-26",
        f"status_{student['id']}": "Absent"
    })

    response = client.get("/reports")

    assert response.status_code == 200
    assert b"Attendance History" in response.data
    assert b"2026-11-26" in response.data


def test_reports_without_attendance(client):
    login(client)
    add_test_student(client)

    response = client.get("/reports")

    assert response.status_code == 200
    assert b"Attendance Analytics" in response.data
    assert b"No attendance history available." in response.data


# ==============================
# ATTENDANCE CSV EXPORT TESTS
# ==============================

def test_attendance_csv_export(client):
    login(client)
    add_test_student(client, "Rahul", "101", "BCA")
    add_test_student(client, "Priya", "102", "BSc")

    response = client.post("/attendance/save", data={
        "date": "2026-11-27",
        "status_1": "Present",
        "status_2": "Absent"
    })

    assert response.status_code == 302

    response = client.get("/attendance/export?date=2026-11-27")

    assert response.status_code == 200
    assert "text/csv" in response.content_type
    assert "attendance_2026-11-27.csv" in response.headers[
        "Content-Disposition"
    ]

    rows = list(csv.reader(
        io.StringIO(response.get_data(as_text=True))
    ))

    assert rows[0] == [
        "Attendance Date",
        "Roll Number",
        "Student Name",
        "Course",
        "Status"
    ]

    assert rows[1] == [
        "2026-11-27", "101", "Rahul", "BCA", "Present"
    ]

    assert rows[2] == [
        "2026-11-27", "102", "Priya", "BSc", "Absent"
    ]


def test_attendance_csv_export_selected_date(client):
    login(client)
    add_test_student(client)

    client.post("/attendance/save", data={
        "date": "2026-11-26",
        "status_1": "Present"
    })

    client.post("/attendance/save", data={
        "date": "2026-11-27",
        "status_1": "Absent"
    })

    response = client.get("/attendance/export?date=2026-11-26")

    assert response.status_code == 200

    rows = list(csv.reader(
        io.StringIO(response.get_data(as_text=True))
    ))

    assert len(rows) == 2
    assert rows[1][0] == "2026-11-26"
    assert rows[1][4] == "Present"


def test_attendance_csv_export_requires_login(client):
    response = client.get("/attendance/export?date=2026-11-27")

    assert response.status_code == 302
    assert "/login" in response.location


def test_attendance_csv_export_invalid_date(client):
    login(client)

    response = client.get("/attendance/export?date=invalid")

    assert response.status_code == 400
    assert b"Invalid attendance date" in response.data
