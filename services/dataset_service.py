"""
Service layer for dataset-related operations used by the Data Science dashboard.
"""

from models.dataset import Dataset


def create_dataset(dataset: Dataset) -> None:
    """Persist a dataset record."""
    dataset.save()


def get_all_datasets():
    """Return all dataset model instances from the DB."""
    return Dataset.get_all()


def get_datasets_by_source(source: str):
    """Filter datasets by their `source` field."""
    return [d for d in Dataset.get_all() if d.source == source]


def update_dataset_size(dataset_id: int, size_mb: float):
    ds = next((d for d in Dataset.get_all() if d.id == dataset_id), None)
    if ds:
        ds.size_mb = size_mb
        ds.save()


def delete_dataset(dataset_id: int):
    ds = next((d for d in Dataset.get_all() if d.id == dataset_id), None)
    if ds:
        ds.delete()
