import sqlite3
conn=sqlite3.connect('data/app.db')
cur=conn.cursor()
for t in ['datasets','it_tickets','cyber_incidents']:
    cur.execute(f'SELECT COUNT(*) FROM {t}')
    print(t, cur.fetchone()[0])
conn.close()
