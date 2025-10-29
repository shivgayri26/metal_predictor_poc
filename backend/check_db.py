import sqlite3
conn = sqlite3.connect('data/metal_prices.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('tables ->', cur.fetchall())
cur.execute("SELECT metal, COUNT(*) FROM metal_prices GROUP BY metal")
print('counts ->', cur.fetchall())
conn.close()
