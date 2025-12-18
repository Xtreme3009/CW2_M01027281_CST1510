from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from database.db_manager import DatabaseManager


@dataclass
class ITTicket:
    """
    Model for service desk tickets used by the IT Operations dashboard.
    """
    id: Optional[int]
    staff: str
    status: str
    category: str
    opened_date: Optional[str]
    closed_date: Optional[str]

    def resolution_days(self) -> Optional[int]:
        """Return resolution time in days between opened and closed dates."""
        if not self.opened_date or not self.closed_date:
            return None
        try:
            opened = datetime.fromisoformat(self.opened_date)
            closed = datetime.fromisoformat(self.closed_date)
        except Exception:
            try:
                opened = datetime.strptime(self.opened_date, "%Y-%m-%d")
                closed = datetime.strptime(self.closed_date, "%Y-%m-%d")
            except Exception:
                return None
        return (closed - opened).days

    def save(self) -> None:
        # Upsert by id so CSV updates replace existing tickets when id provided
        db = DatabaseManager()
        db.execute(
            "INSERT OR REPLACE INTO it_tickets (id, staff, status, category, opened_date, closed_date) VALUES (?, ?, ?, ?, ?, ?)",
            (self.id, self.staff, self.status, self.category, self.opened_date, self.closed_date),
        )

    def delete(self) -> None:
        if not self.id:
            return
        db = DatabaseManager()
        db.execute("DELETE FROM it_tickets WHERE id = ?", (self.id,))

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "ITTicket":
        return cls(
            id=row.get("id"),
            staff=row.get("staff"),
            status=row.get("status"),
            category=row.get("category"),
            opened_date=row.get("opened_date"),
            closed_date=row.get("closed_date"),
        )

    @classmethod
    def get_all(cls) -> List["ITTicket"]:
        db = DatabaseManager()
        rows = db.fetch_all("SELECT * FROM it_tickets")
        return [cls.from_row(r) for r in rows]
