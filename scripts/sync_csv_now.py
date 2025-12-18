import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from database.db_manager import DatabaseManager
import time

csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cyber_incidents.csv')
csv_path = os.path.abspath(csv_path)

df_csv = pd.read_csv(csv_path)
# Normalize id
if 'incident_id' in df_csv.columns and 'id' not in df_csv.columns:
    df_csv['id'] = df_csv['incident_id']
df_csv['id'] = pd.to_numeric(df_csv.get('id'), errors='coerce')

# Normalize resolved_date
if 'resolved_date' in df_csv.columns:
    df_csv['resolved_date'] = df_csv['resolved_date'].replace(['NA', 'Na', 'N/A', 'nan', 'NaN'], pd.NA)

# Deduplicate
if df_csv.get('id').notna().any():
    df_csv = df_csv.drop_duplicates(subset=['id'])
else:
    df_csv = df_csv.drop_duplicates()

# Write to DB
DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')
DB = os.path.abspath(DB)
db = DatabaseManager(db_path=DB)
conn = db.connect()
cur = conn.cursor()
cur.execute('DELETE FROM cyber_incidents')
for idx, row in df_csv.iterrows():
    cid = int(row['id']) if pd.notna(row.get('id')) else None
    typ = (row.get('category') or '').strip()
    sev = (row.get('severity') or '').strip()
    status = (row.get('status') or '').strip()
    reported = row.get('reported_date') or None
    resolved = row.get('resolved_date') if pd.notna(row.get('resolved_date')) else None
    if cid is not None:
        cur.execute("INSERT INTO cyber_incidents (id, type, severity, status, reported_date, resolved_date) VALUES (?, ?, ?, ?, ?, ?)", (cid, typ, sev, status, reported, resolved))
    else:
        cur.execute("INSERT INTO cyber_incidents (type, severity, status, reported_date, resolved_date) VALUES (?, ?, ?, ?, ?)", (typ, sev, status, reported, resolved))
conn.commit()
conn.close()
print('Synced CSV to DB at', time.ctime())
