import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE attendance ADD COLUMN edited_by_admin INTEGER DEFAULT 0")
    print("✅ Column 'edited_by_admin' added")
except:
    print("ℹ️ Column already exists")

conn.commit()
conn.close()
