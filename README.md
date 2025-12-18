# CW2 Project — Multi-Dashboard App

A compact Streamlit-based multi-dashboard application that integrates lightweight persistence, CSV-driven data sync, and an optional AI assistant. The app provides role-based dashboards for Cybersecurity, Data Science, and IT Operations.

Contents
- `app.py` — Streamlit launcher and role-based navigation.
- `Dashboards/` — Dashboard views: `Cybersecurity`, `Data_Science`, `IT_Operations`, and `Login` UI.
- `models/` — Domain models (`User`, `CyberIncident`, `Dataset`, `ITTicket`) with simple save/delete/get methods.
- `services/` — Thin service wrappers and an `ai_service` that talks to OpenAI-compatible endpoints via HTTP.
- `database/` — `db_manager.py` helper and `init_db.py` schema initializer.
- `data/` — CSV files used as the canonical source for each dashboard (e.g., `data/cyber_incidents.csv`).

Quick start
1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Initialize the databases (creates `data/app.db` and `data/auth.db`):

Recommended (module mode):

```powershell
python -m database.init_db
```

Or (from the `database/` folder):

```powershell
cd database
python init_db.py
cd ..
```

3. Configure environment variables (optional but required for the AI assistant):

```powershell
#$Env:OPENAI_API_KEY = "sk-..."
```

You may also create a `.env` file at the repository root and the app will load it via `python-dotenv`.

4. Run the app locally:

```powershell
python -m streamlit run app.py
```

Features
- Role-based dashboards: users see dashboards according to their `role` (Admin, Cybersecurity, Data Science, IT Operations).
- CSV-driven sync: dashboards read CSVs in `data/` and synchronize into `data/app.db` on change detection.
	- `Cybersecurity` uses a dedupe-and-replace sync to avoid duplicate accumulation; it preserves explicit `id` values when present.
	- `Data Science` and `IT Operations` syncs will remove DB rows not present in the CSV when the CSV includes explicit `id` values.
- Persistence: lightweight SQLite files in `data/` (`app.db` for records; `auth.db` for user auth).
- Authentication: registration and login via the `Login` dashboard; passwords are hashed with `bcrypt` and stored in `data/auth.db`.
- AI assistant: the `Cybersecurity` dashboard can call an OpenAI-compatible chat completion endpoint using `services/ai_service.py` (reads `OPENAI_API_KEY`).

Dependencies
The main dependencies are in `requirements.txt`. Key packages used in the codebase:
- `streamlit` — Web UI
- `pandas` — CSV handling and dataframes
- `plotly` — Visualizations
- `requests` — HTTP calls to AI endpoints
- `python-dotenv` — `.env` support
- `bcrypt` — Password hashing (required)

If you want to use the official `openai` SDK instead of the generic HTTP wrapper, add `openai` to `requirements.txt` and update `services/ai_service.py` accordingly.

Architecture notes
- Models in `models/` are intentionally lightweight and perform direct DB operations via `database/db_manager.py`.
- `database/init_db.py` currently creates the expected tables; if you modify the schema, update service/model callers accordingly.
- CSV-based workflows treat CSVs as the authoritative source by default. If you prefer incremental upserts instead of full-table sync, implement an incremental sync policy in the corresponding `Dashboards/` module.

Auth & Users
- User records live in `data/auth.db` and are managed by the `User` model. You can register via the `Login` dashboard UI.
- Roles: `Admin` (access to all dashboards), `Cybersecurity`, `Data Science`, `IT Operations`.

CSV sync behavior and cautions
- The dashboards automatically sync CSV files on detection of a newer modification time. This can overwrite DB contents for the synced tables.
- Back up your CSVs and DB prior to large edits if you need to preserve history.

Troubleshooting
- Missing `README_OPENAI.md`: some earlier docs referenced `README_OPENAI.md` — it is optional. If you rely on AI calls, ensure `OPENAI_API_KEY` is set and you have network access.
- Login failures: ensure `bcrypt` is installed and that stored `password_hash` values are valid. Use the registration flow to create a new user.
- DB table errors when running `database/init_db.py`: run it via module mode (`python -m database.init_db`) if you hit relative import issues.

Development
- Add dashboards by following the pattern in `Dashboards/`; read CSV, sync to DB, then render Streamlit UI.
- Tests and helper scripts are available in `scripts/` for inspecting and syncing CSVs.

Contributing
- Fork, create a feature branch, add tests or scripts under `scripts/` for complex flows, and open a PR.

License & Contact
- This repository is provided as-is for course work and demonstration. Modify and extend as needed.

---
If you'd like, I can also:
- add a minimal `README_OPENAI.md` with best-practices for API keys and prompts,
- pin exact package versions in `requirements.txt`, or
- add an admin UI for user management.
Tell me which one to do next.
