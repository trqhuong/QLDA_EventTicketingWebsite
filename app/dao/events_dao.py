from app.models import Event, Artist, City, District, EventArtist, EventType

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

def get_districts_by_city(city_id):
    """Get districts for a specific city"""
    return District.query.filter_by(city_id=city_id).all()

def get_all_event_types():
    return EventType.query.all()
