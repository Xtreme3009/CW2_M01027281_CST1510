import sys, os, shutil, subprocess, json
import pandas as pd
import sqlite3
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA = os.path.join(ROOT, 'data')
DB = os.path.join(DATA, 'app.db')

# Ensure imports work
sys.path.append(ROOT)

# Paths
cyber_csv = os.path.join(DATA, 'cyber_incidents.csv')
datasets_csv = os.path.join(DATA, 'datasets.csv')
it_csv = os.path.join(DATA, 'it_tickets.csv')

backups = {}

def backup(fp):
    b = fp + '.bak'
    shutil.copy(fp, b)
    backups[fp] = b

def restore(fp):
    if fp in backups:
        bak = backups[fp]
        if os.path.exists(bak):
            shutil.move(bak, fp)
        else:
            print(f"Warning: backup not found for {fp}: {bak}")

def sync_cyber():
    subprocess.check_call([sys.executable, os.path.join(ROOT, 'scripts', 'sync_csv_now.py')])

def sync_others():
    subprocess.check_call([sys.executable, os.path.join(ROOT, 'scripts', 'sync_other_csvs.py')])

def query(sql):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return rows

report = {'cyber': [], 'datasets': [], 'it': []}

# Backup CSVs
for f in [cyber_csv, datasets_csv, it_csv]:
    backup(f)

try:
    # --- CYBER: remove last row and sync ---
    df = pd.read_csv(cyber_csv)
    orig_len = len(df)
    removed = df.iloc[-1:].to_dict(orient='records')[0]
    df2 = df.iloc[:-1]
    df2.to_csv(cyber_csv, index=False)
    sync_cyber()
    # collect report
    total = query('SELECT COUNT(*) FROM cyber_incidents')[0][0]
    monthly = query("SELECT month, COUNT(*) FROM (SELECT date(reported_date) as month FROM cyber_incidents) GROUP BY month")
    report['cyber'].append({'action': 'removed last row', 'orig_len': orig_len, 'db_total': total, 'monthly_sample': monthly[:5]})

    # restore from backup (to then test adding)
    restore(cyber_csv)

    # --- CYBER: append a new row and sync ---
    df = pd.read_csv(cyber_csv)
    new_id = int(df['id'].max()) + 100
    new_row = {
        'id': new_id,
        'category': 'TestCat',
        'severity': 'Low',
        'reported_date': datetime.now().strftime('%Y-%m-%d'),
        'status': 'Open',
        'resolved_date': ''
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(cyber_csv, index=False)
    sync_cyber()
    total = query('SELECT COUNT(*) FROM cyber_incidents')[0][0]
    types = query("SELECT type, COUNT(*) FROM cyber_incidents GROUP BY type ORDER BY COUNT(*) DESC LIMIT 5")
    report['cyber'].append({'action': 'appended new row', 'new_id': new_id, 'db_total': total, 'top_types': types})

    # restore original cyber csv
    restore(cyber_csv)
    sync_cyber()

    # --- DATASETS: remove last row and sync ---
    df = pd.read_csv(datasets_csv)
    orig_len = len(df)
    removed_ds = df.iloc[-1:].to_dict(orient='records')[0]
    df2 = df.iloc[:-1]
    df2.to_csv(datasets_csv, index=False)
    sync_others()
    total = query('SELECT COUNT(*) FROM datasets')[0][0]
    sources = query('SELECT source, COUNT(*) FROM datasets GROUP BY source')
    report['datasets'].append({'action': 'removed last row', 'orig_len': orig_len, 'db_total': total, 'sources_sample': sources[:5]})

    restore(datasets_csv)

    # append new dataset row
    df = pd.read_csv(datasets_csv)
    new_id = int(df['id'].max()) + 100 if 'id' in df.columns and pd.notna(df['id'].max()) else None
    new_row = {
        'id': new_id,
        'dataset_name': 'test_dataset_x',
        'source': 'test_source',
        'size_mb': 12.34,
        'rows': 1234,
        'upload_date': datetime.now().strftime('%Y-%m-%d')
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(datasets_csv, index=False)
    sync_others()
    total = query('SELECT COUNT(*) FROM datasets')[0][0]
    report['datasets'].append({'action': 'appended new row', 'new_id': new_id, 'db_total': total})

    restore(datasets_csv)
    sync_others()

    # --- IT TICKETS: remove last row and sync ---
    df = pd.read_csv(it_csv)
    orig_len = len(df)
    removed_it = df.iloc[-1:].to_dict(orient='records')[0]
    df2 = df.iloc[:-1]
    df2.to_csv(it_csv, index=False)
    sync_others()
    total = query('SELECT COUNT(*) FROM it_tickets')[0][0]
    staff = query('SELECT staff, COUNT(*) FROM it_tickets GROUP BY staff')
    report['it'].append({'action': 'removed last row', 'orig_len': orig_len, 'db_total': total, 'staff_sample': staff[:5]})

    restore(it_csv)

    # append new ticket row
    df = pd.read_csv(it_csv)
    new_id = int(df['id'].max()) + 100 if 'id' in df.columns and pd.notna(df['id'].max()) else None
    new_row = {
        'id': new_id,
        'staff': 'tester',
        'status': 'Open',
        'category': 'test',
        'opened_date': datetime.now().strftime('%Y-%m-%d'),
        'closed_date': ''
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(it_csv, index=False)
    sync_others()
    total = query('SELECT COUNT(*) FROM it_tickets')[0][0]
    report['it'].append({'action': 'appended new row', 'new_id': new_id, 'db_total': total})

    restore(it_csv)
    sync_others()

finally:
    # Ensure all backups restored if any remain
    for orig, bak in backups.items():
        try:
            if os.path.exists(bak):
                shutil.move(bak, orig)
        except Exception as e:
            print(f"Failed to restore backup {bak} -> {orig}: {e}")

# Print final report
print(json.dumps(report, indent=2, default=str))
