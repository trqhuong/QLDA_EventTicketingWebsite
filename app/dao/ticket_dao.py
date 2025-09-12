from app.models import Ticket
from app import db

def get_tickets_by_event_id(event_id = None):
    query = Ticket.query.filter(Ticket.event_id.__eq__(event_id))

    return query.all()

def get_ticket_by_ticket_id(ticket_id = None):
    return db.session.get(Ticket,ticket_id)