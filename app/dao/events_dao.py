from app.models import Event

def get_events_by_category(category=None):
    query = Event.query
    if category:
        query = query.filter_by(Type=category)
    return query.all()