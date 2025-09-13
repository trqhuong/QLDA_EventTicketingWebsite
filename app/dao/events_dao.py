from exceptiongroup import catch

from app.models import Event, Artist, City, District, EventArtist, EventType, Ticket, TicketStatus
from app import db
from datetime import datetime, time, date
from app.models import TypeTicket

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
                             image_url, date, time, organizer_id, ticket_data):
    """Tạo sự kiện mới với thông tin tickets"""
    try:
        # Chuyển đổi string date và time thành đối tượng date và time
        if isinstance(date, str):
            event_start_date = datetime.strptime(date, '%Y-%m-%d').date()
        else:
            event_start_date = date

        if isinstance(time, str):
            event_start_time = datetime.strptime(time, '%H:%M').time()
        else:
            event_start_time = time

        # Tạo sự kiện mới
        new_event = Event(
            name=name,
            city_id=city_id,
            district_id=district_id,
            address=address,
            event_type_id=event_type_id,
            description=description,
            image=image_url,
            date=event_start_date,
            time=event_start_time,
            organizer_id=organizer_id
        )

        db.session.add(new_event)
        db.session.flush()  # Để có event.id

        # Tạo tickets với đúng tên field
        ticket_prices = ticket_data['prices']
        ticket_quantities = ticket_data['quantities']
        ticket_descriptions = ticket_data['descriptions']
        ticket_types = ticket_data.get('types', [])  # Lấy ticket types từ form

        for i in range(len(ticket_prices)):
            if ticket_prices[i]:  # Kiểm tra tên ticket không rỗng

                # Xử lý ticket type
                ticket_type = TypeTicket.Standard  # Default
                if i < len(ticket_types) and ticket_types[i]:
                    if ticket_types[i] == 'VIP':
                        ticket_type = TypeTicket.VIP
                    else:
                        ticket_type = TypeTicket.Standard
                new_ticket = Ticket(
                    status=TicketStatus.Available,
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
    event_type = EventType.query.get(event.event_type_id)
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
        'address': event.address,
        'description': event.description,
        'type': event_type.name,
        'location': location_info,
        'image_url' : event.image
    }
    return event_details

def get_events_by_organizer(organizer_id, page=1, per_page=6, status_filter=None):
    """Lấy tất cả sự kiện của một nhà tổ chức với phân trang và lọc theo trạng thái"""
    from datetime import date
    today = date.today()

    query = Event.query.filter(Event.organizer_id == organizer_id)

    # Lọc theo trạng thái
    if status_filter == 'upcoming':  # Sắp diễn ra
        query = query.filter(Event.date > today)
    elif status_filter == 'ongoing':  # Đang diễn ra
        query = query.filter(Event.date == today)
    elif status_filter == 'completed':  # Đã kết thúc
        query = query.filter(Event.date < today)

    # Sắp xếp theo ngày (mới nhất trước)
    query = query.order_by(Event.date.desc())

    return query.paginate(page=page, per_page=per_page, error_out=False)
