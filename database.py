import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ---------------- ADMIN TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    password TEXT
)
""")

# ---------------- TEACHERS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT
)
""")

# ---------------- STUDENTS TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll_no TEXT UNIQUE,
    email TEXT
)
""")

# ---------------- ATTENDANCE TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    teacher_id INTEGER,
    subject TEXT,
    date TEXT,
    status TEXT
)
""")

# ---------------- INSERT ADMIN ----------------
cursor.execute("DELETE FROM admin")
cursor.execute(
    "INSERT INTO admin (name, password) VALUES (?, ?)",
    ("ALI", "ali410")
)

# ---------------- INSERT TEACHERS ----------------
cursor.execute("DELETE FROM teachers")

teachers = [
    ("Sajid Ali", "sajidali@gmail.com", "sajid123"),
    ("M Irtaza", "irtaza@gmail.com", "irtaza539"),
    ("Shahbaz Wasti", "shahbaz@gmail.com", "shahbaz456"),
    ("Ghulam Jillani", "ghulam@gmail.com", "jillani789")
]

cursor.executemany(
    "INSERT INTO teachers (name, email, password) VALUES (?, ?, ?)",
    teachers
)

# ---------------- INSERT STUDENTS ----------------
cursor.execute("DELETE FROM students")

students = [
    ("Ali", "BSF230001", "ali@gmail.com"),
    ("Ahmed", "BSF230002", "ahmed@gmail.com"),
    ("Bilal", "BSF230003", "bilal@gmail.com"),
    ("Hassan", "BSF230004", "hassan@gmail.com"),
    ("Usman", "BSF230005", "usman@gmail.com"),
    ("Zain", "BSF230006", "zain@gmail.com"),
    ("Hamza", "BSF230007", "hamza@gmail.com"),
    ("Ayesha", "BSF230008", "ayesha@gmail.com"),
    ("Sara", "BSF230009", "sara@gmail.com"),
    ("Hira", "BSF230010", "hira@gmail.com"),
    ("Nida", "BSF230011", "nida@gmail.com"),
    ("Fatima", "BSF230012", "fatima@gmail.com"),
    ("Khadija", "BSF230013", "khadija@gmail.com"),
    ("Asad", "BSF230014", "asad@gmail.com"),
    ("Taha", "BSF230015", "taha@gmail.com"),
    ("Areeba", "BSF230016", "areeba@gmail.com"),
    ("Sana", "BSF230017", "sana@gmail.com"),
    ("Ibrahim", "BSF230018", "ibrahim@gmail.com"),
    ("Rafay", "BSF230019", "rafay@gmail.com"),
    ("Daniyal", "BSF230020", "daniyal@gmail.com"),
    ("Umair Akhtar", "BSF230021", "meoumair945@gmail.com"),
    ("Faizan Shafqat", "BSF230022", "faizanshafqat.se@gmail.com"),
    ("Zohaib Raza", "BSF230023", "khan5201319@gmail.com")
]

cursor.executemany(
    "INSERT INTO students (name, roll_no, email) VALUES (?, ?, ?)",
    students
)

conn.commit()
conn.close()

print("✅ Database created successfully with Admin, Teachers, and Students")
