import sqlite3, os

db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'turinix.db')
if not os.path.exists(db_path):
    print('DB not found at', db_path)
    raise SystemExit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
rows = cur.fetchall()
print('Tables:')
for r in rows:
    print('-', r[0])
conn.close()
