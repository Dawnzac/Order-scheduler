import sqlite3, json, os

db_path = os.path.join(os.path.dirname(__file__), '..', 'instance', 'turinix.db')
if not os.path.exists(db_path):
    print('DB not found at', db_path)
    raise SystemExit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute("SELECT id, scheduled_time, status, recurrence_type, next_execution_at FROM scheduled_orders ORDER BY rowid DESC LIMIT 10")
rows = cur.fetchall()
print(json.dumps(rows, default=str, indent=2))
conn.close()
