
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

students = []

@app.route("/")
def home():
    return render_template("index.html", students=students)

@app.route("/add", methods=["POST"])
def add_student():
    name = request.form.get("name")
    roll = request.form.get("roll")
    course = request.form.get("course")

    if name and roll and course:
        students.append({
            "name": name,
            "roll": roll,
            "course": course
        })

    return redirect(url_for("home"))

@app.route("/delete/<int:index>")
def delete_student(index):
    if 0 <= index < len(students):
        students.pop(index)

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
