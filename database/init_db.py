from database.db_manager import DatabaseManager


def init_db():
    """
    Initialize application SQLite databases and required tables.

    Creates the main application DB at `data/app.db`.
    """
    # Main application DB (data/app.db)
    main_db = DatabaseManager(db_path="data/app.db")
    main_db.execute("""
    CREATE TABLE IF NOT EXISTS cyber_incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        severity TEXT,
        status TEXT,
        reported_date TEXT,
        resolved_date TEXT
    )
    """)

    main_db.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY,
        dataset_name TEXT,
        source TEXT,
        size_mb REAL,
        rows INTEGER,
        upload_date TEXT
    )
    """)

    main_db.execute("""
    CREATE TABLE IF NOT EXISTS it_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff TEXT,
        status TEXT,
        category TEXT,
        opened_date TEXT,
        closed_date TEXT
    )
    """)

    # Authentication DB (separate file for usernames/passwords)
    auth_db = DatabaseManager(db_path="data/auth.db")
    auth_db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT,
        role TEXT
    )
    """)


if __name__ == "__main__":
    init_db()
    print("Databases initialized successfully (data/app.db and data/auth.db).")
