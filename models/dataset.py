from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from database.db_manager import DatabaseManager


@dataclass
class Dataset:
    """
    This model provides convenience helpers used by the Data Science
    dashboard and simple persistence methods (save/delete/get_all).
    """
    id: Optional[int]
    dataset_name: str
    source: str
    size_mb: float
    rows: int
    upload_date: Optional[str]

    def size_category(self) -> str:
        """Categorize dataset size for governance decisions."""
        if self.size_mb < 100:
            return "Small"
        elif self.size_mb < 1000:
            return "Medium"
        return "Large"

    def is_archive_candidate(self) -> bool:
        """Simple rule-based archiving logic used by the UI."""
        return self.size_mb > 1000 and self.rows < 100000

    def save(self) -> None:
        # Perform an upsert so CSV re-exports with the same id overwrite DB rows.
        db = DatabaseManager()
        db.execute(
            "INSERT OR REPLACE INTO datasets (id, dataset_name, source, size_mb, rows, upload_date) VALUES (?, ?, ?, ?, ?, ?)",
            (self.id, self.dataset_name, self.source, self.size_mb, self.rows, self.upload_date),
        )

    def delete(self) -> None:
        if not self.id:
            return
        db = DatabaseManager()
        db.execute("DELETE FROM datasets WHERE id = ?", (self.id,))

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "Dataset":
        # Convert a DB row/dict to a Dataset instance.
        return cls(
            id=row.get("id"),
            dataset_name=row.get("dataset_name") or row.get("name"),
            source=row.get("source"),
            size_mb=row.get("size_mb") or 0.0,
            rows=row.get("rows") or 0,
            upload_date=row.get("upload_date"),
        )

    @classmethod
    def get_all(cls) -> List["Dataset"]:
        db = DatabaseManager()
        rows = db.fetch_all("SELECT * FROM datasets")
        return [cls.from_row(r) for r in rows]
