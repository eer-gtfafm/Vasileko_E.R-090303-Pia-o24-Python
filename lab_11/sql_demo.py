import sqlite3
from pathlib import Path

con = sqlite3.connect("hotel.db")
con.row_factory = sqlite3.Row
queries = Path("queries.sql").read_text(encoding="utf-8")

parts = []
current = []
for line in queries.splitlines():
    if line.strip().startswith("-- ") and current:
        parts.append((current[0], "\n".join(current[1:])))
        current = []
    current.append(line)
if current:
    parts.append((current[0], "\n".join(current[1:])))

for title, sql in parts:
    print("=" * 70)
    print(title)
    print("=" * 70)
    try:
        rows = con.execute(sql).fetchall()
    except Exception as e:
        print("ОШИБКА:", e)
        continue
    if not rows:
        print("(пустой результат)")
        continue
    cols = rows[0].keys()
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    print(header)
    print("-" * len(header))
    for r in rows:
        print(" | ".join(str(r[c]).ljust(widths[c]) for c in cols))
    print()
