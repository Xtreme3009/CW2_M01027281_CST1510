# Project Technical Report — Draft

## 1. Introduction

This document is a working draft of the technical report for the multi-dashboard Streamlit app. It summarises architecture, design choices (OOP refactor), AI integration, and diagrams to include.

## 2. Architecture Overview
- Frontend: Streamlit dashboards in `Dashboards/`.
- Persistence: SQLite via `database/db_manager.py` and `database/init_db.py`.
- Business logic: `services/` (thin wrappers) and domain models in `models/` (OOP refactor).
- AI: `services/ai_service.py` calls OpenAI Chat Completions.

## 3. Domain Model (OOP)
- `User` — id, username, password_hash, role; save/delete/get_by_username
- `CyberIncident` — id, type, severity, status, reported_date, resolved_date; resolution_time_days(), save(), delete()
- `Dataset` — id, dataset_name, source, size_mb, rows, upload_date; size_category(), save(), delete()
- `ITTicket` — id, staff, status, category, opened_date, closed_date; resolution_days(), save(), delete()

## 4. Diagrams to include
- Entity Relationship Diagram (ERD) of SQLite tables
- Class diagram for `models/` showing methods and relations
- Sequence diagram for AI Assistant: UI -> ai_service -> OpenAI -> UI

## 5. Implementation Notes
- Services were refactored to delegate responsibilities to model methods to centralize business logic and simplify unit testing.
- `services/ai_service.py` wraps the HTTP call and raises `AIServiceError` for callers to handle.

## 6. Next steps
- Produce ERD and class diagrams (draw and attach PNGs in `docs/diagrams/`).
- Expand unit tests for model save/load behavior.
- Finalise written report with screenshots and evaluation.

# Project Summary & MVP Terms

Summary
-------
This project implements a compact Streamlit Multi‑Domain Intelligence Platform that ingests canonical CSV sources, synchronises them into local SQLite databases, and presents role‑based dashboards for Cybersecurity, Data Science, and IT Operations. The platform provides user registration/login, interactive Plotly visualisations, CSV↔DB sync logic, and a lightweight AI assistant integrated into the Cybersecurity dashboard for contextual guidance.

MVP Terms (what to claim and defend)
-----------------------------------

- Scope
	- Primary domain: **Cybersecurity** (Tier 2 — operational dashboard with authentication, persistence, visual analytics, and an AI helper).
	- Canonical data: CSV files in `data/` (e.g., `data/cyber_incidents.csv`) synchronised into `data/app.db` and user auth in `data/auth.db`.

- Core features (deliverables)
	- **Authentication:** registration/login with `bcrypt` hashed passwords stored in `data/auth.db`.
	- **Persistence:** SQLite DB accessed via `database/db_manager.py`; domain models in `models/` implement `save()/get_all()/delete()`.
	- **CSV sync:** dashboards detect CSV modification time and sync deduplicated rows into the DB (preserving explicit `id` values when present).
	- **Visualisations:** interactive Plotly charts (time series, severity area, status pie, category trends) rendered in Streamlit.
	- **AI Assistant:** Chat completion wrapper in `services/ai_service.py` that uses `OPENAI_API_KEY` for contextual cybersecurity guidance.
	- **Role-based UI:** `app.py` routes users to dashboards per role; Admin can access all dashboards.

- Acceptance criteria (how to prove it works)
	- A registered user can log in and only see dashboards permitted by their role.
	- Editing a CSV under `data/` causes a detectable sync and updates DB counts and dashboard charts.
	- Charts render correctly for both monthly aggregations and the daily fallback when months are sparse.
	- The AI assistant returns a reply when `OPENAI_API_KEY` is set or reports a clear error otherwise.

- Minimal tests / checks to demonstrate functionality
	- Register a test user and verify login flow and role-restricted views.
	- Modify `data/cyber_incidents.csv` (add and remove a row), confirm DB counts change and dashboard charts update.
	- Set `OPENAI_API_KEY` and verify the assistant returns a helpful reply.
	- Confirm `requirements.txt` includes `bcrypt`, `streamlit`, `pandas`, `plotly`, `requests`, and `python-dotenv`.

- Architecture claims to state briefly
	- MVC-like separation: `models/` (Model), `Dashboards/` (View), `services/` + dashboard handlers (Controller).
	- OOP benefit: models encapsulate SQL and business logic, improving maintainability and testability.
	- Security: `bcrypt` for password hashing and environment-based API keys (no plaintext secrets in repo).

- Limitations / assumptions to acknowledge
	- Single-file SQLite persistence is not suitable for high-concurrency production loads.
	- CSV-authoritative sync replaces or overwrites table contents by design; incremental upserts are left as future work.
	- The AI assistant uses a simple HTTP wrapper (requests) — rate limits and network availability are external constraints.

- Suggested next steps (discussion / future work)
	- Add an Admin UI for user management and scheduled sync tasks.
	- Implement transactional, incremental upserts with change logging to preserve audit history.
	- Add automated unit tests and CI checks for sync, auth, and plotting flows.

How to use this content
-----------------------
Use the Summary as your report introduction. Convert each bullet under "MVP Terms" into a short subsection for System Architecture, Implementation, Validation, and Conclusion. The Acceptance Criteria and Minimal Tests can be used as a Methods / Validation section to demonstrate the app functions.

---
If you'd like, I can now: produce a one‑page checklist, draft starter paragraphs for each report section, or implement one of the suggested next steps. Tell me which you prefer.
