"""
Service helpers for IT ticket operations. Ensures dashboard code remains concise.
"""

from models.it_ticket import ITTicket


def create_ticket(ticket: ITTicket) -> None:
    ticket.save()


def get_all_tickets():
    return ITTicket.get_all()


def update_ticket_status(ticket_id: int, status: str):
    tickets = ITTicket.get_all()
    t = next((x for x in tickets if x.id == ticket_id), None)
    if t:
        t.status = status
        t.save()


def delete_ticket(ticket_id: int):
    tickets = ITTicket.get_all()
    t = next((x for x in tickets if x.id == ticket_id), None)
    if t:
        t.delete()
