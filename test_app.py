
import pytest
from app import app, students


@pytest.fixture
def client():
    app.config["TESTING"] = True

    students.clear()

    with app.test_client() as client:
        yield client

    students.clear()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Student Management System" in response.data


def test_add_student(client):
    response = client.post("/add", data={
        "name": "Rahul",
        "roll": "101",
        "course": "BCA"
    })

    assert response.status_code == 302
    assert len(students) == 1
    assert students[0]["name"] == "Rahul"


def test_delete_student(client):
    students.append({
        "name": "Priya",
        "roll": "102",
        "course": "BSc IT"
    })

    response = client.get("/delete/0")

    assert response.status_code == 302
    assert len(students) == 0


def test_add_student_missing_details(client):
    response = client.post("/add", data={
        "name": "Arjun",
        "roll": "",
        "course": "BTech"
    })

    assert response.status_code == 302
    assert len(students) == 0
