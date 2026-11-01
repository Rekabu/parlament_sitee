import sqlite3

conn = sqlite3.connect('parliament.db')
cur = conn.cursor()

# Список таблиц
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print("Таблицы:", tables)

# Схема таблицы user
cur.execute("PRAGMA table_info(user)")
print("\nКолонки в user:")
for row in cur.fetchall():
    print(row)

conn.close()