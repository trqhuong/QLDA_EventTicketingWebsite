from app.models import Event, Artist, City, District, EventArtist, EventType, Ticket
from app import db
from datetime import datetime, time, date

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

def create_event(name, city_id, district_id, address, event_type_id, description, date, time, organizer_id):
    """Tạo sự kiện mới"""
    try:
        # Chuyển đổi string date và time thành đối tượng date và time
        if isinstance(date, str):
            event_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            event_date = date
            
        if isinstance(time, str):
            event_time = datetime.strptime(time, '%H:%M').time()
        else:
            event_time = time
        
        new_event = Event(
            name=name,
            city_id=city_id,
            district_id=district_id,
            address=address,
            event_type_id=event_type_id,
            description=description,
            date=event_date,
            time=event_time,
            organizer_id=organizer_id
        )
        
        db.session.add(new_event)
        db.session.commit()
        return new_event
    except Exception as e:
        db.session.rollback()
        raise e

def create_event_with_tickets(name, city_id, district_id, address, event_type_id, description, 
                             image_url, start_date, start_time, end_date, end_time, 
                             organizer_id, ticket_data):
    """Tạo sự kiện mới với thông tin tickets"""
    try:
        # Chuyển đổi string date và time thành đối tượng date và time
        if isinstance(start_date, str):
            event_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            event_start_date = start_date
            
        if isinstance(start_time, str):
            event_start_time = datetime.strptime(start_time, '%H:%M').time()
        else:
            event_start_time = start_time
        
        # Xử lý end_date và end_time (có thể null)
        event_end_date = None
        event_end_time = None
        
        if end_date:
            if isinstance(end_date, str):
                event_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                event_end_date = end_date
                
        if end_time:
            if isinstance(end_time, str):
                event_end_time = datetime.strptime(end_time, '%H:%M').time()
            else:
                event_end_time = end_time
        
        # Tạo sự kiện mới
        new_event = Event(
            name=name,
            city_id=city_id,
            district_id=district_id,
            address=address,
            event_type_id=event_type_id,
            description=description,
            image=image_url,
            startDate=event_start_date,
            startTime=event_start_time,
            endDate=event_end_date,
            endTime=event_end_time,
            organizer_id=organizer_id
        )
        
        db.session.add(new_event)
        db.session.flush()  # Để có event.id
        
        # Tạo tickets với đúng tên field
        ticket_names = ticket_data['names']
        ticket_prices = ticket_data['prices']
        ticket_quantities = ticket_data['quantities']
        ticket_descriptions = ticket_data['descriptions']
        ticket_types = ticket_data.get('types', [])  # Lấy ticket types từ form

        for i in range(len(ticket_names)):
            if ticket_names[i]:  # Kiểm tra tên ticket không rỗng
                # Import TypeTicket để convert string thành enum
                from app.models import TypeTicket

                # Xử lý ticket type
                ticket_type = TypeTicket.Standard  # Default
                if i < len(ticket_types) and ticket_types[i]:
                    if ticket_types[i] == 'VIP':
                        ticket_type = TypeTicket.VIP
                    else:
                        ticket_type = TypeTicket.Standard

                new_ticket = Ticket(
                    name=ticket_names[i],  # Sử dụng field name
                    description=ticket_descriptions[i] if i < len(ticket_descriptions) else None,  # Sử dụng field description
                    type=ticket_type,
                    price=ticket_prices[i] if i < len(ticket_prices) else 0,
                    quantity=ticket_quantities[i] if i < len(ticket_quantities) else 1,
                    event_id=new_event.id
                )
                db.session.add(new_ticket)
        
        db.session.commit()
        return new_event
        
    except Exception as e:
        db.session.rollback()
        raise e

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
        'type': event.event_type.name,
        'location': location_info,
        'image_url' : event.image_url
    }
    return event_details;
