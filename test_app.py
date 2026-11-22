
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
