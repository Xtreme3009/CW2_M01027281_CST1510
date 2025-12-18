"""
IT Operations dashboard view.

Displays service desk KPIs and visualisations sourced from
`data/it_tickets.csv` which is synced to the `it_tickets` table.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dataclasses import asdict
from models.it_ticket import ITTicket
import os
import time


def dashboard():
    st.title("IT Operations Performance Dashboard")

    # --- Auto-sync CSV to DB when file changed since last sync ---
    csv_path = "data/it_tickets.csv"
    try:
        mtime = os.path.getmtime(csv_path)
    except Exception:
        mtime = None

    prev_mtime = st.session_state.get("it_csv_mtime")
    if mtime and (prev_mtime is None or mtime > prev_mtime):
        df_csv = pd.read_csv(csv_path)
        save_errors = []
        ids_in_csv = []
        for idx, row in df_csv.iterrows():
            try:
                closed_date = row.closed_date if pd.notna(row.closed_date) else None
            except Exception:
                closed_date = None
            try:
                row_id = int(row.id) if "id" in row.index and pd.notna(row.id) else None
                ticket = ITTicket(
                    id=row_id,
                    staff=row.get("staff") or "",
                    status=row.get("status") or "",
                    category=row.get("category") or "",
                    opened_date=row.get("opened_date") or None,
                    closed_date=closed_date,
                )
                ticket.save()
                if row_id is not None:
                    ids_in_csv.append(row_id)
            except Exception as e:
                save_errors.append(f"row {idx}: {e}")

        # If CSV provided ids, remove DB rows whose id is not present in the CSV
        if ids_in_csv:
            from database.db_manager import DatabaseManager
            dbm = DatabaseManager()
            placeholders = ",".join(["?" for _ in ids_in_csv])
            try:
                dbm.execute(f"DELETE FROM it_tickets WHERE id NOT IN ({placeholders})", tuple(ids_in_csv))
            except Exception:
                pass

        st.session_state["it_csv_mtime"] = mtime
        if save_errors:
            st.error("Errors occurred while syncing CSV to DB. Showing first messages:")
            for msg in save_errors[:10]:
                st.write(msg)
        else:
            st.success(f"Synced CSV to DB ({time.ctime(mtime)})")

    # --- Fetch latest data from model ---
    tickets = ITTicket.get_all()
    df = pd.DataFrame([asdict(t) for t in tickets])

    if df.empty:
        st.warning("No tickets data available.")
        return

    st.subheader("Service Desk Tickets")
    st.dataframe(df)

    # --- Resolution time ---
    df["opened_date"] = pd.to_datetime(df["opened_date"])
    df["closed_date"] = pd.to_datetime(df["closed_date"])
    df["resolution_days"] = (df["closed_date"] - df["opened_date"]).dt.days

    # --- Average resolution by status ---
    status_delay = df.groupby("status")["resolution_days"].mean().reset_index()
    fig1 = px.bar(
        status_delay,
        x="status",
        y="resolution_days",
        title="Average Resolution Time by Status"
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- Tickets per staff ---
    staff_count = df["staff"].value_counts().reset_index()
    staff_count.columns = ["Staff", "Tickets"]
    fig2 = px.bar(
        staff_count,
        x="Staff",
        y="Tickets",
        title="Tickets Handled per Staff"
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- Tickets trend over time (monthly) ---
    if "opened_date" in df.columns:
        try:
            df["opened_month"] = df["opened_date"].dt.to_period("M").dt.to_timestamp()
            monthly_tickets = df.groupby("opened_month").size().reset_index(name="count")
            if monthly_tickets.empty:
                st.info("No ticket opening data to plot over time.")
            else:
                fig_trend = px.line(monthly_tickets, x="opened_month", y="count", title="Tickets Opened Over Time (Monthly)")
                st.plotly_chart(fig_trend, use_container_width=True)
        except Exception as e:
            st.error(f"Could not plot tickets over time: {e}")
    else:
        st.info("Opened date column missing; cannot plot tickets over time.")

    # --- Resolution time distribution ---
    res_dist = df[~df["resolution_days"].isna()]["resolution_days"]
    if not res_dist.empty:
        fig_hist = px.histogram(res_dist, nbins=30, title="Resolution Time Distribution (days)")
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- SLA compliance (example SLA: resolution within 7 days) ---
    sla_days = st.sidebar.number_input("SLA days (resolution)", min_value=1, max_value=90, value=7)
    sla_compliant = df[~df["resolution_days"].isna()]["resolution_days"].le(sla_days).mean()
    st.metric("SLA Compliance (<= {} days)".format(sla_days), f"{sla_compliant:.0%}")

    # --- Key percentiles for resolution ---
    pctiles = res_dist.quantile([0.5, 0.75, 0.9]).to_dict() if not res_dist.empty else {}
    cols = st.columns(3)
    cols[0].metric("Median Resolution (days)", f"{int(pctiles.get(0.5, 0))}")
    cols[1].metric("75th Percentile (days)", f"{int(pctiles.get(0.75, 0))}")
    cols[2].metric("90th Percentile (days)", f"{int(pctiles.get(0.9, 0))}")

    st.success("Dashboard updated from CSV and database automatically.")
