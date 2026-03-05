import os
import smtplib
from email.message import EmailMessage


def send_absent_email(to_email, student_name, roll_no, subject, date, teacher_name):
    EMAIL_ADDRESS = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return False, "Email credentials not found"

    try:
        msg = EmailMessage()
        msg["Subject"] = "Absence Notification"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        msg.set_content(f"""
Dear {student_name},

Roll No: {roll_no}

You were ABSENT in today's class.

📅 Date: {date}
📘 Subject: {subject}
👨‍🏫 Teacher: {teacher_name}

If this is a mistake, please contact the admin.

Regards,
Attendance Management System
""")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        return True, "Email sent successfully"

    except Exception as e:
        return False, str(e)
