from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from database.db_manager import DatabaseManager
import sqlite3


def _ensure_users_table():
    """Ensure the users table exists in the auth DB."""
    db = DatabaseManager(db_path="data/auth.db")
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            role TEXT
        )
        """
    )


@dataclass
class User:
    """
    User domain model for authentication and role management.

    Passwords are stored as bcrypt hashes in the `password_hash` field.
    This class handles simple CRUD operations against the auth DB.
    """
    id: Optional[int]
    username: str
    password_hash: str
    role: str

    @property
    def is_cybersecurity(self) -> bool:
        return self.role.lower() == "cybersecurity"

    @property
    def is_data_science(self) -> bool:
        return self.role.lower() == "data science"

    @property
    def is_it_operations(self) -> bool:
        return self.role.lower() == "it operations"

    def save(self) -> None:
        """Insert or update the user record in the database."""
        _ensure_users_table()
        db = DatabaseManager(db_path="data/auth.db")
        if self.id:
            db.execute(
                "UPDATE users SET username=?, password_hash=?, role=? WHERE id=?",
                (self.username, self.password_hash, self.role, self.id),
            )
        else:
            db.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (self.username, self.password_hash, self.role),
            )

    def delete(self) -> None:
        """Delete this user from the database."""
        if not self.id:
            return
        _ensure_users_table()
        db = DatabaseManager(db_path="data/auth.db")
        db.execute("DELETE FROM users WHERE id = ?", (self.id,))

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "User":
        # sqlite3.Row does not implement .get(), convert to dict first
        try:
            if hasattr(row, "keys") and not isinstance(row, dict):
                row = dict(row)
        except Exception:
            pass
        return cls(id=row.get("id"), username=row.get("username"), password_hash=row.get("password_hash"), role=row.get("role"))

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        _ensure_users_table()
        db = DatabaseManager(db_path="data/auth.db")
        try:
            rows = db.execute("SELECT * FROM users WHERE username = ?", (username,), fetch=True)
        except sqlite3.OperationalError:
            # If table is still missing for any reason, try to create and return None
            _ensure_users_table()
            return None
        if not rows:
            return None
        return cls.from_row(rows[0])

    @classmethod
    def get_all(cls) -> List["User"]:
        _ensure_users_table()
        db = DatabaseManager(db_path="data/auth.db")
        try:
            rows = db.fetch_all("SELECT * FROM users")
        except sqlite3.OperationalError:
            _ensure_users_table()
            return []
        return [cls.from_row(r) for r in rows]
