"""
Service layer for cybersecurity incident operations.

These thin wrappers keep dashboard code concise and encapsulate
common CRUD operations on the `CyberIncident` model.
"""

from models.cyber_incident import CyberIncident


def create_incident(incident: CyberIncident) -> None:
    """Persist a new incident or update an existing one."""
    incident.save()


def get_all_incidents():
    """Return a list of all CyberIncident objects from the DB."""
    return CyberIncident.get_all()


def get_incidents_by_type(incident_type: str):
    """Filter incidents by their `type` field."""
    return [i for i in CyberIncident.get_all() if i.type == incident_type]


def update_incident_status(incident_id: int, status: str):
    """Update the status of a specific incident if it exists."""
    incidents = CyberIncident.get_all()
    inc = next((i for i in incidents if i.id == incident_id), None)
    if inc:
        inc.status = status
        inc.save()


def delete_incident(incident_id: int):
    """Delete an incident by id (no-op if not found)."""
    incidents = CyberIncident.get_all()
    inc = next((i for i in incidents if i.id == incident_id), None)
    if inc:
        inc.delete()
