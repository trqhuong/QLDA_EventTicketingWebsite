from app.models import Ticket


def get_tickets_by_event_id(event_id = None):
    query = Ticket.query.filter(Ticket.event_id.__eq__(event_id))

    return query.all()
