import sqlite3

conn = sqlite3.connect('app.db')
c = conn.cursor()
tables = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("Tables:", tables)
conn.close()
