"""
Data Science dashboard view.

Provides dataset inventory, size and row-count visualisations.
The dashboard reads `data/datasets.csv` and synchronises it into the`datasets` table so the UI reflects CSV edits.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dataclasses import asdict
from models.dataset import Dataset
import os
import time


def dashboard():
    st.title("Data Science Governance Dashboard")

    # --- Auto-sync CSV to DB when file changed since last sync ---
    csv_path = "data/datasets.csv"
    try:
        mtime = os.path.getmtime(csv_path)
    except Exception:
        mtime = None

    prev_mtime = st.session_state.get("datasets_csv_mtime")
    if mtime and (prev_mtime is None or mtime > prev_mtime):
        df_csv = pd.read_csv(csv_path)
        save_errors = []
        ids_in_csv = []
        for idx, row in df_csv.iterrows():
            try:
                row_id = int(row.id) if "id" in row.index and pd.notna(row.id) else None
                ds = Dataset(
                    id=row_id,
                    dataset_name=row.get("dataset_name") or row.get("name") or "",
                    source=row.get("source") or "",
                    size_mb=float(row.get("size_mb") or 0.0),
                    rows=int(row.get("rows") or 0),
                    upload_date=row.get("upload_date") or None,
                )
                ds.save()
                if row_id is not None:
                    ids_in_csv.append(row_id)
            except Exception as e:
                save_errors.append(f"row {idx}: {e}")

        # If CSV provided ids, remove DB rows whose id is not present in the CSV
        if ids_in_csv:
            db = Dataset.__module__  # avoid lint; we'll get DatabaseManager below
            from database.db_manager import DatabaseManager
            dbm = DatabaseManager()
            # Build parameter placeholders safely
            placeholders = ",".join(["?" for _ in ids_in_csv])
            try:
                dbm.execute(f"DELETE FROM datasets WHERE id NOT IN ({placeholders})", tuple(ids_in_csv))
            except Exception:
                # In case of unexpected schema, ignore and continue
                pass

        st.session_state["datasets_csv_mtime"] = mtime
        if save_errors:
            st.error("Errors occurred while syncing CSV to DB. Showing first messages:")
            for msg in save_errors[:10]:
                st.write(msg)
        else:
            st.success(f"Synced CSV to DB ({time.ctime(mtime)})")

    # --- Fetch latest data from model ---
    datasets = Dataset.get_all()
    df = pd.DataFrame([asdict(d) for d in datasets])

    st.subheader("Dataset Inventory")
    st.dataframe(df)

    # --- Total Size by Source ---
    if not df.empty:
        size_by_source = df.groupby("source")["size_mb"].sum().reset_index()
        fig1 = px.bar(size_by_source, x="source", y="size_mb", title="Total Dataset Size by Source (MB)")
        st.plotly_chart(fig1, use_container_width=True)

        # --- Dataset Size vs Rows ---
        fig2 = px.scatter(df, x="rows", y="size_mb", size="size_mb", color="source",
                          title="Dataset Size vs Rows")
        st.plotly_chart(fig2, use_container_width=True)

    st.success("Dashboard updated from CSV and database automatically.")
