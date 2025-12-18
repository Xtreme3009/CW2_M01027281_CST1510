import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
from models.dataset import Dataset
from models.it_ticket import ITTicket

# Sync datasets
csv1 = os.path.join(os.path.dirname(__file__), '..', 'data', 'datasets.csv')
csv1 = os.path.abspath(csv1)
df = pd.read_csv(csv1)
for idx, row in df.iterrows():
    ds = Dataset(
        id=int(row.id) if 'id' in row.index and pd.notna(row.id) else None,
        dataset_name=row.get('dataset_name') or row.get('name') or '',
        source=row.get('source') or '',
        size_mb=float(row.get('size_mb') or 0.0),
        rows=int(row.get('rows') or 0),
        upload_date=row.get('upload_date') or None,
    )
    ds.save()

# Sync it_tickets
csv2 = os.path.join(os.path.dirname(__file__), '..', 'data', 'it_tickets.csv')
csv2 = os.path.abspath(csv2)
df2 = pd.read_csv(csv2)
for idx, row in df2.iterrows():
    try:
        closed_date = row.closed_date if pd.notna(row.closed_date) else None
    except Exception:
        closed_date = None
    ticket = ITTicket(
        id=int(row.id) if 'id' in row.index and pd.notna(row.id) else None,
        staff=row.get('staff') or '',
        status=row.get('status') or '',
        category=row.get('category') or '',
        opened_date=row.get('opened_date') or None,
        closed_date=closed_date,
    )
    ticket.save()

print('Synced datasets and it_tickets CSV to DB')
