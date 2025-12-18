"""Utility to validate the grouping logic used by the Cybersecurity dashboard.

This script loads incidents from the DB, computes monthly/daily groupings
and attempts to construct Plotly figures to ensure the plotting code
works outside of Streamlit.
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.cyber_incident import CyberIncident
from dataclasses import asdict
import pandas as pd


incidents = CyberIncident.get_all()
print('Loaded incidents:', len(incidents))
if not incidents:
    raise SystemExit('No incidents')

df = pd.DataFrame([asdict(i) for i in incidents])
print('Columns:', df.columns.tolist())

# Prepare dates
df['reported_date'] = pd.to_datetime(df['reported_date'], errors='coerce')
df = df.dropna(subset=['reported_date'])
df['month'] = df['reported_date'].dt.to_period('M').dt.to_timestamp()
print('After date parse, rows:', len(df))

# monthly
monthly = df.groupby('month').size().reset_index(name='count')
print('Monthly groups:', len(monthly))
print(monthly.head())

# severity over time
if 'severity' in df.columns:
    sev_time = df.groupby(['month','severity']).size().reset_index(name='count')
    print('Severity-time groups:', len(sev_time))
    print(sev_time.head())

# top categories trends
if 'type' in df.columns:
    top_categories = df['type'].value_counts().nlargest(5).index.tolist()
    print('Top categories:', top_categories)
    top_df = df[df['type'].isin(top_categories)]
    cat_trends = top_df.groupby(['month','type']).size().reset_index(name='count')
    print('Category trends groups:', len(cat_trends))
    print(cat_trends.head())
    # Try creating plotly figures to check for errors
    import plotly.express as px
    fig_time = px.line(monthly, x='month', y='count', title='Incidents Over Time (Monthly)')
    fig_sev = px.area(sev_time, x='month', y='count', color='severity', title='Severity Distribution')
    fig_cat = px.line(cat_trends, x='month', y='count', color='type', title='Top Categories Trends')
    print('Created figures:', type(fig_time), type(fig_sev), type(fig_cat))
