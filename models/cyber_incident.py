from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from database.db_manager import DatabaseManager

DB_PATH = "data/app.db"


@dataclass
class CyberIncident:
    """
      `save()` inserts or updates a record.
      `delete()` removes a record by id.
      `resolution_time_days()` computes days between reported and resolved dates.
      `get_all()` loads all incidents from the DB (class method).
    """
    id: Optional[int]
    type: str
    severity: str
    status: str
    reported_date: Optional[str]
    resolved_date: Optional[str] = None

    def save(self):
        # Upsert behavior: INSERT if no id, otherwise UPDATE the existing row.
        db = DatabaseManager()
        if self.id is None:
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO cyber_incidents
                (type, severity, status, reported_date, resolved_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.type, self.severity, self.status,
                 self.reported_date, self.resolved_date)
            )
            conn.commit()
            # Populate id with the auto-assigned row id for caller convenience.
            self.id = cursor.lastrowid
            conn.close()
        else:
            db.execute(
                """
                UPDATE cyber_incidents
                SET type = ?, severity = ?, status = ?, reported_date = ?, resolved_date = ?
                WHERE id = ?
                """,
                (self.type, self.severity, self.status,
                 self.reported_date, self.resolved_date, self.id)
            )

    def delete(self) -> None:
        """Delete this incident from the DB (no-op if id is None)."""
        if self.id is None:
            return
        db = DatabaseManager(db_path=DB_PATH)
        db.execute("DELETE FROM cyber_incidents WHERE id = ?", (self.id,))

    def resolution_time_days(self) -> Optional[int]:
        """Return resolution time in days (if both dates are present).

        Returns None if either date is missing or cannot be parsed.
        """
        if not self.reported_date or not self.resolved_date:
            return None
        try:
            start = datetime.fromisoformat(self.reported_date)
            end = datetime.fromisoformat(self.resolved_date)
            return (end - start).days
        except Exception:
            return None

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "CyberIncident":
        # Convert DB row/dict into a CyberIncident instance.
        return cls(
            id=row["id"],
            type=row["type"],
            severity=row["severity"],
            status=row["status"],
            reported_date=row["reported_date"],
            resolved_date=row["resolved_date"],
        )

    @classmethod
    def get_all(cls):
        db = DatabaseManager()
        rows = db.fetch_all(
            "SELECT * FROM cyber_incidents ORDER BY reported_date"
        )
        return [cls.from_row(r) for r in rows]
