
import os
import sqlite3
import psycopg
from psycopg.rows import dict_row

SQLITE_BACKUP = os.path.join(
    os.path.expanduser("~"),
    "Desktop",
    "students_backup.sqlite3"
)

DATABASE_URL = os.environ["DATABASE_URL"]

# Check SQLite backup
if not os.path.exists(SQLITE_BACKUP):
    raise FileNotFoundError(SQLITE_BACKUP)

source = sqlite3.connect(SQLITE_BACKUP)
source.row_factory = sqlite3.Row

students = source.execute(
    "SELECT id, name, roll, course FROM students"
).fetchall()

admins = source.execute(
    "SELECT id, username, password_hash FROM admins"
).fetchall()

print("SQLite students:", len(students))
print("SQLite admins:", len(admins))

try:
    with psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    ) as target:

        # Create tables if they do not exist
        target.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                roll TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL
            )
        """)

        target.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)

        # Avoid accidental migration into a populated database
        existing = target.execute(
            "SELECT COUNT(*) AS count FROM students"
        ).fetchone()["count"]

        if existing:
            raise RuntimeError(
                "Target database already contains students. "
                "Migration stopped to protect existing data."
            )

        # Migrate students, preserving IDs
        for student in students:
            target.execute("""
                INSERT INTO students (id, name, roll, course)
                VALUES (%s, %s, %s, %s)
            """, (
                student["id"],
                student["name"],
                student["roll"],
                student["course"]
            ))

        # Migrate admins, preserving password hashes
        for admin in admins:
            target.execute("""
                INSERT INTO admins (id, username, password_hash)
                VALUES (%s, %s, %s)
                ON CONFLICT (username)
                DO UPDATE SET password_hash = EXCLUDED.password_hash
            """, (
                admin["id"],
                admin["username"],
                admin["password_hash"]
            ))

        # Reset auto-increment sequences
        target.execute("""
            SELECT setval(
                pg_get_serial_sequence('students', 'id'),
                COALESCE((SELECT MAX(id) FROM students), 1),
                EXISTS(SELECT 1 FROM students)
            )
        """)

        target.execute("""
            SELECT setval(
                pg_get_serial_sequence('admins', 'id'),
                COALESCE((SELECT MAX(id) FROM admins), 1),
                EXISTS(SELECT 1 FROM admins)
            )
        """)

        student_count = target.execute(
            "SELECT COUNT(*) AS count FROM students"
        ).fetchone()["count"]

        admin_count = target.execute(
            "SELECT COUNT(*) AS count FROM admins"
        ).fetchone()["count"]

    print("\nMigration completed!")
    print("PostgreSQL students:", student_count)
    print("PostgreSQL admins:", admin_count)

finally:
    source.close()
