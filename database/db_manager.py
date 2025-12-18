import sqlite3


class DatabaseManager:
    """
    `execute` for running statements and
    `fetch_all` for returning query results as a list of dicts.
    """

    def __init__(self, db_path="data/app.db"):
        self.db_path = db_path

    def connect(self):
        # Create a sqlite3 connection and configure rows to be accessible
        # as mapping objects (sqlite3.Row) so callers can use keys.
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, query, params=(), fetch=False):
        """Execute a SQL statement. Set `fetch=True` to return rows."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        data = cursor.fetchall() if fetch else None
        conn.close()
        return data

    def fetch_all(self, query, params=()):
        """Execute a SELECT and return rows as list[dict]."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
