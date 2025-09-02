from app.models import Event, Artist, City, District, EventArtist, EventType


def get_events_by_category(category=None):
    query = Event.query
    if category:
        query = query.filter_by(Type=category)
    return query.all()

def get_all_artists():
    return Artist.query.all()

def get_all_locations():
    return City.query.all()

def get_all_events(page=1, per_page=3, event_type_id=None, city_id=None, artist_id=None, kw=None):
    query = Event.query

    if event_type_id:
        query = query.filter(Event.event_type_id == event_type_id)

    if city_id:
        query = query.filter(Event.city_id == city_id)

    if artist_id:
        # nếu Event có quan hệ many-to-many với Artist
        query = query.join(EventArtist).filter(Artist.id == artist_id)

    if kw:
        query = query.filter(Event.name.ilike(f'%{kw}%'))

    return query.paginate(page=page, per_page=per_page, error_out=False)

def get_events_by_artist(artist_id):
    """Get events by artist ID"""
    return Event.query.join(EventArtist).filter(EventArtist.artist_id == artist_id).all()

def get_events_by_location(city_id):
    """Get events by city ID"""
    return Event.query.filter(Event.city_id == city_id).all()

def get_artists_with_events():
    """Get artists who have events scheduled"""
    return Artist.query.join(EventArtist).distinct().all()

def get_cities_with_events():
    """Get cities that have events"""
    return City.query.join(Event).distinct().all()

def get_districts_by_city(city_id):
    """Get districts for a specific city"""
    return District.query.filter_by(city_id=city_id).all()

def get_all_event_types():
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
