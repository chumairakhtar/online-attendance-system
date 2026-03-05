from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_attendance_pdf(filename, title, attendance_rows):
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, title)

    c.setFont("Helvetica", 10)
    y = height - 100

    c.drawString(50, y, "Name")
    c.drawString(200, y, "Roll No")
    c.drawString(300, y, "Subject")
    c.drawString(420, y, "Status")

    y -= 20

    for row in attendance_rows:
        if y < 50:
            c.showPage()
            y = height - 50

        c.drawString(50, y, row["name"])
        c.drawString(200, y, row["roll_no"])
        c.drawString(300, y, row["subject"])
        c.drawString(420, y, row["status"])

        y -= 18

    c.save()
