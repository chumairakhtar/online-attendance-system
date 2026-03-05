from flask import Flask, render_template, request, redirect, url_for, session, send_file
from dotenv import load_dotenv
load_dotenv()

import sqlite3
from datetime import date, datetime, timedelta
from utils.email_sender import send_absent_email
from utils.pdf_generator import generate_attendance_pdf

app = Flask(__name__)
app.secret_key = "attendance_secret_key"


# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# ====================================================
# LOGIN SELECTION
# ====================================================
@app.route("/")
def index():
    return render_template("index.html")


# ====================================================
# ADMIN LOGIN
# ====================================================
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        conn = get_db_connection()
        admin = conn.execute(
            "SELECT * FROM admin WHERE name=? AND password=?",
            (name, password)
        ).fetchone()
        conn.close()

        if admin:
            session.clear()
            session["admin_id"] = admin["id"]
            return redirect(url_for("admin_dashboard"))
        else:
            return "❌ Invalid Admin Credentials"

    return render_template("admin_login.html")


# ====================================================
# ADMIN DASHBOARD
# ====================================================
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))
    return render_template("admin_dashboard.html")
#======================================================
#VIEW ATTANDANCE
#======================================================

@app.route("/admin/attendance")
def admin_attendance():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    records = conn.execute("""
        SELECT attendance.id, students.name, students.roll_no,
               attendance.subject, attendance.status, attendance.date,
               attendance.edited_by_admin
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        ORDER BY attendance.date DESC
    """).fetchall()
    conn.close()

    return render_template("admin_attendance_edit.html", records=records)
#======================================================================================
#EDIT ATTANDANCE
#======================================================================================
@app.route("/admin/update-attendance/<int:att_id>/<string:new_status>")
def admin_update_attendance(att_id, new_status):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.execute("""
        UPDATE attendance
        SET status=?, edited_by_admin=1
        WHERE id=?
    """, (new_status, att_id))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_attendance"))

# ====================================================
# ADMIN → TEACHERS
# ====================================================
@app.route("/admin/teachers")
def admin_teachers():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    teachers = conn.execute("SELECT * FROM teachers").fetchall()
    conn.close()

    return render_template("admin_teachers.html", teachers=teachers)


@app.route("/admin/add_teacher", methods=["POST"])
def admin_add_teacher():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO teachers (name, email, password) VALUES (?, ?, ?)",
        (request.form["name"], request.form["email"], request.form["password"])
    )
    conn.commit()
    conn.close()

    return redirect(url_for("admin_teachers"))


@app.route("/admin/delete_teacher/<int:id>")
def admin_delete_teacher(id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM teachers WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_teachers"))


# ====================================================
# ADMIN → STUDENTS
# ====================================================
@app.route("/admin/students")
def admin_students():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template("admin_students.html", students=students)


@app.route("/admin/add_student", methods=["POST"])
def admin_add_student():
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO students (name, roll_no, email) VALUES (?, ?, ?)",
        (request.form["name"], request.form["roll_no"], request.form["email"])
    )
    conn.commit()
    conn.close()

    return redirect(url_for("admin_students"))


@app.route("/admin/delete_student/<int:id>")
def admin_delete_student(id):
    if "admin_id" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_students"))


# ====================================================
# TEACHER LOGIN
# ====================================================
@app.route("/teacher", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        conn = get_db_connection()
        teacher = conn.execute(
            "SELECT * FROM teachers WHERE email=? AND password=?",
            (request.form["email"], request.form["password"])
        ).fetchone()
        conn.close()

        if teacher:
            session.clear()
            session["teacher_id"] = teacher["id"]
            session["teacher_name"] = teacher["name"]
            return redirect(url_for("teacher_dashboard"))
        else:
            return "❌ Invalid Teacher Credentials"

    return render_template("teacher_login.html")


# ====================================================
# TEACHER DASHBOARD
# ====================================================
@app.route("/teacher/dashboard")
def teacher_dashboard():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))
    return render_template("teacher_dashboard.html")


# ====================================================
# MARK ATTENDANCE (EMAIL VERIFIED)
# ====================================================
@app.route("/teacher/mark-attendance", methods=["GET", "POST"])
def mark_attendance():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))

    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()

    if request.method == "POST":
        subject = request.form["subject"]
        class_name = request.form["class"]
        session_name = request.form["session"]
        shift = request.form["shift"]

        today = date.today().strftime("%d-%m-%Y")
        teacher_name = session["teacher_name"]

        for s in students:
            status = request.form.get(f"status_{s['id']}")

            conn.execute("""
                INSERT INTO attendance 
                (student_id, subject, class, session, shift, status, date, teacher)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["id"], subject, class_name, session_name,
                shift, status, today, teacher_name
            ))

            if status == "Absent":
                success, msg = send_absent_email(
                    s["email"], s["name"], s["roll_no"],
                    subject, today, teacher_name
                )

                if success:
                    print(f"✅ Email sent to {s['email']}")
                else:
                    print(f"❌ Email failed for {s['email']} → {msg}")

        conn.commit()
        conn.close()
        return "<h3>Attendance submitted successfully.</h3>"

    conn.close()
    return render_template("mark_attendance.html", students=students)



# ====================================================
# WEEKLY PDF REPORT
# ====================================================
@app.route("/teacher/weekly-report")
def weekly_report():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))

    week_ago = datetime.today() - timedelta(days=7)

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT students.name, students.roll_no, attendance.subject, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        WHERE attendance.date >= ?
    """, (week_ago.strftime("%d-%m-%Y"),)).fetchall()
    conn.close()

    filename = "weekly_attendance.pdf"
    generate_attendance_pdf(filename, "Weekly Attendance Report", rows)
    return send_file(filename, as_attachment=True)


# ====================================================
# MONTHLY PDF REPORT
# ====================================================
@app.route("/teacher/monthly-report")
def monthly_report():
    if "teacher_id" not in session:
        return redirect(url_for("teacher_login"))

    month_start = datetime.today().replace(day=1)

    conn = get_db_connection()
    rows = conn.execute("""
        SELECT students.name, students.roll_no, attendance.subject, attendance.status
        FROM attendance
        JOIN students ON attendance.student_id = students.id
        WHERE attendance.date >= ?
    """, (month_start.strftime("%d-%m-%Y"),)).fetchall()
    conn.close()

    filename = "monthly_attendance.pdf"
    generate_attendance_pdf(filename, "Monthly Attendance Report", rows)
    return send_file(filename, as_attachment=True)


# ====================================================
# LOGOUT
# ====================================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ====================================================
# RUN
# ====================================================
if __name__ == "__main__":
    app.run(debug=True)
app.run(host="0.0.0.0", port=10000)
#if __name__ == "__main__":
  #  app.run(debug=True)