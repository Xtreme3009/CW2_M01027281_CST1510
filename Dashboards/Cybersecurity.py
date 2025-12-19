"""
Cybersecurity dashboard view.

This dashboard shows incident listings, time series and severity
breakdowns. It also provides a lightweight AI assistant that uses the
`services.ai_service` wrapper to query an LLM for guidance.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from dataclasses import asdict
from models.cyber_incident import CyberIncident
from services.ai_service import chat_completion, AIServiceError
from database.db_manager import DatabaseManager
import os
import time

# --- Ensure database table exists ---
db = DatabaseManager()
db.execute("""
CREATE TABLE IF NOT EXISTS cyber_incidents (
    id INTEGER PRIMARY KEY,
    type TEXT,
    severity TEXT,
    status TEXT,
    reported_date TEXT,
    resolved_date TEXT
)
""")

def dashboard():
    st.title("Cybersecurity Dashboard")

    # --- Auto-sync CSV to DB when file changed since last sync ---
    csv_path = "data/cyber_incidents.csv"
    try:
        mtime = os.path.getmtime(csv_path)
    except Exception:
        mtime = None

    prev_mtime = st.session_state.get("cyber_csv_mtime")
    if mtime and (prev_mtime is None or mtime > prev_mtime):
        df_csv = pd.read_csv(csv_path)

        # Normalize id column (accept 'id' or 'incident_id')
        if 'incident_id' in df_csv.columns and 'id' not in df_csv.columns:
            df_csv['id'] = df_csv['incident_id']
        df_csv['id'] = pd.to_numeric(df_csv.get('id'), errors='coerce')

        # Normalize resolved_date values like 'NA' or 'Na' to missing
        if 'resolved_date' in df_csv.columns:
            df_csv['resolved_date'] = df_csv['resolved_date'].replace(['NA', 'Na', 'N/A', 'nan', 'NaN'], pd.NA)

        # Deduplicate: prefer explicit ids when present, otherwise dedupe by full row
        if df_csv.get('id').notna().any():
            df_csv = df_csv.drop_duplicates(subset=['id'])
        else:
            df_csv = df_csv.drop_duplicates()

        # Replace DB contents with deduped CSV rows to avoid accumulation of duplicates
        conn = db.connect()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM cyber_incidents")
            for idx, row in df_csv.iterrows():
                cid = int(row['id']) if pd.notna(row.get('id')) else None
                typ = (row.get('category') or '').strip()
                sev = (row.get('severity') or '').strip()
                status = (row.get('status') or '').strip()
                reported = row.get('reported_date') or None
                resolved = row.get('resolved_date') if pd.notna(row.get('resolved_date')) else None

                if cid is not None:
                    cur.execute(
                        "INSERT INTO cyber_incidents (id, type, severity, status, reported_date, resolved_date) VALUES (?, ?, ?, ?, ?, ?)",
                        (cid, typ, sev, status, reported, resolved)
                    )
                else:
                    cur.execute(
                        "INSERT INTO cyber_incidents (type, severity, status, reported_date, resolved_date) VALUES (?, ?, ?, ?, ?)",
                        (typ, sev, status, reported, resolved)
                    )
            conn.commit()
            st.session_state["cyber_csv_mtime"] = mtime
            st.success(f"Synced CSV to DB successfully ({time.ctime(mtime)})")
        except Exception as e:
            conn.rollback()
            st.error(f"Failed to sync CSV to DB: {e}")
        finally:
            conn.close()

    # --- Fetch all incidents ---
    incidents = CyberIncident.get_all()
    df = pd.DataFrame([asdict(i) for i in incidents])

    if df.empty:
        st.warning("No incident data available.")
        return

    st.subheader("All Incidents")
    st.dataframe(df)

    # --- Prepare dates ---
    df["reported_date"] = pd.to_datetime(df["reported_date"], errors="coerce")
    df = df.dropna(subset=["reported_date"])
    df["month"] = df["reported_date"].dt.to_period("M").dt.to_timestamp()

    # --- Incidents over time (monthly) ---
    try:
        monthly = df.groupby("month").size().reset_index(name="count")
        if not monthly.empty:
            if len(monthly) < 2:
                # Fallback to daily trend when only a single month exists
                daily = df.groupby(df["reported_date"].dt.date).size().reset_index(name="count")
                daily.columns = ["date", "count"]
                fig_time = px.line(daily, x="date", y="count", title="Incidents Over Time (Daily)")
            else:
                fig_time = px.line(monthly, x="month", y="count", title="Incidents Over Time (Monthly)")
            st.plotly_chart(fig_time, use_container_width=True)
    except Exception as e:
        st.error(f"Could not plot incidents over time: {e}")

    # --- Severity distribution over time ---
    if "severity" in df.columns:
        try:
            sev_time = df.groupby(["month", "severity"]).size().reset_index(name="count")
            if not sev_time.empty:
                if sev_time["month"].nunique() < 2:
                    # Fallback to daily severity distribution
                    sev_daily = df.groupby([df["reported_date"].dt.date, "severity"]).size().reset_index(name="count")
                    sev_daily.columns = ["date", "severity", "count"]
                    fig_sev = px.area(sev_daily, x="date", y="count", color="severity",
                                      title="Severity Distribution Over Time (Daily)")
                else:
                    fig_sev = px.area(sev_time, x="month", y="count", color="severity",
                                      title="Severity Distribution Over Time")
                st.plotly_chart(fig_sev, use_container_width=True)
        except Exception as e:
            st.error(f"Could not plot severity distribution: {e}")

    # --- Status breakdown ---
    if "status" in df.columns:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_status = px.pie(status_counts, names="Status", values="Count", title="Incident Status Breakdown")
        st.plotly_chart(fig_status, use_container_width=True)

    # --- Top categories and trends ---
    if "type" in df.columns:
        try:
            top_categories = df["type"].value_counts().nlargest(5).index.tolist()
            if top_categories:
                top_df = df[df["type"].isin(top_categories)]
                cat_trends = top_df.groupby(["month", "type"]).size().reset_index(name="count")
                if not cat_trends.empty:
                    if cat_trends["month"].nunique() < 2:
                        # Fallback to daily category trends
                        cat_daily = top_df.groupby([top_df["reported_date"].dt.date, "type"]).size().reset_index(name="count")
                        cat_daily.columns = ["date", "type", "count"]
                        fig_cat = px.line(cat_daily, x="date", y="count", color="type",
                                          title="Top Categories Trends (Daily)")
                    else:
                        fig_cat = px.line(cat_trends, x="month", y="count", color="type",
                                          title="Top Categories Trends")
                    st.plotly_chart(fig_cat, use_container_width=True)
        except Exception as e:
            st.error(f"Could not plot top categories trends: {e}")

    # --- Severity counts overall ---
    if "severity" in df.columns:
        severity_counts = df["severity"].value_counts().reset_index()
        severity_counts.columns = ["Severity", "Count"]
        fig2 = px.bar(severity_counts, x="Severity", y="Count", title="Incidents by Severity")
        st.plotly_chart(fig2, use_container_width=True)

    # --- Quick KPIs ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Incidents", int(len(df)))
    critical_count = int((df["severity"].str.lower() == "critical").sum()) if "severity" in df.columns else 0
    col2.metric("Critical Incidents", critical_count)
    open_count = int((df["status"].str.lower() == "open").sum()) if "status" in df.columns else 0
    col3.metric("Open Incidents", open_count)

    st.success("Dashboard updated from CSV and database automatically.")

    # --- AI Assistant ---
    with st.expander("AI Assistant — ask for security advice or explain statistics"):
        st.write("Ask a question like: 'Which categories increased in the last 3 months?' or 'How to prioritise critical incidents?'")
        user_input = st.text_area("Your question", value="", height=120)
        ask_btn = st.button("Ask AI")
        if ask_btn and user_input.strip():
            with st.spinner("Contacting AI assistant..."):
                try:
                    system_prompt = (
                        "You are a concise cybersecurity analyst. Provide practical, safety-minded guidance. "
                        "When giving recommendations, be explicit about steps and risk considerations. "
                        "If asked about data, explain how to compute the metric from incident records."
                    )
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input},
                    ]
                    reply = chat_completion(messages)
                    st.markdown("**AI Assistant:**")
                    st.write(reply)
                except AIServiceError as e:
                    if "quota" in str(e).lower():
                        st.error("Daily AI quota reached. Please try again tomorrow.")
                    else:
                        st.error(f"AI assistant error: {e}")
                except Exception as e:
                    st.error(f"Unexpected error calling AI assistant: {e}")

