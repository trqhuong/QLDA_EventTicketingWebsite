from app.models import Event

def get_events_by_category(category=None):
    query = Event.query
    if category:
        query = query.filter_by(type=category)
    return query.all()


def get_details_by_event_id(event_id = None):

    event = Event.query.get(event_id)
    if(not event):
        return None

    location_info = {
        'city' : event.city.name,
        'district' : event.district.name,
    }
    event_details = {
        'event_id': event.id,
        'name': event.name,
        'time': event.time.strftime('%H:%M'),
        'date': event.date.strftime('%d-%m-%Y'),
        'description': event.description,
        'type': event.type.name,
        'location': location_info
    }
    return event_details;