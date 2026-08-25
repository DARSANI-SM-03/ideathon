import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "studiq.db")
print(f"Inspecting database at: {db_path}")

if not os.path.exists(db_path):
    print("Database file does not exist yet!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    tables = [t[0] for t in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
    print(f"\nTotal Tables ({len(tables)}):")
    for t in sorted(tables):
        if not t.startswith("sqlite_"):
            count = cursor.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  - {t}: {count} rows")

    print("\nUsers / Accounts Summary:")
    for role_table in ["students", "parents", "mentors", "teachers", "admins"]:
        if role_table in tables:
            rows = cursor.execute(f"SELECT * FROM {role_table} LIMIT 5").fetchall()
            cols = [d[0] for d in cursor.description]
            print(f"\nTable '{role_table}' ({len(rows)} sample rows):")
            print(f"  Columns: {cols}")
            for r in rows:
                print(f"  Row: {r}")
