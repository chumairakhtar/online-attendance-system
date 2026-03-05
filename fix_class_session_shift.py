import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

columns = ["class", "session", "shift"]

for col in columns:
    try:
        cur.execute(f"ALTER TABLE attendance ADD COLUMN {col} TEXT")
        print(f"✅ Column '{col}' added")
    except:
        print(f"ℹ️ Column '{col}' already exists")

conn.commit()
conn.close()
