import unittest
from datetime import date

from app import app, db
from app.models import User, Organizer, Role, ReviewStatus, Ticket, TypeTicket, TicketStatus
from app.dao.events_dao import get_all_events,get_details_by_event_id, create_event_with_tickets, get_events_by_organizer


class Event(unittest.TestCase):
    def setUp(self):
        # Tạo context Flask và reset database test
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def test_get_all_events_no_filter(app_context):
        # Lấy tất cả event, không truyền filter
        events = get_all_events()
        assert events is not None
        assert events.total >= 1  # đảm bảo trong DB có ít nhất 1 event

    def test_get_all_events_filter_by_event_type(app_context):
        # Ví dụ event_type_id = 1 (Âm nhạc)
        events = get_all_events(event_type_id=1)
        for e in events.items:
            assert e.event_type_id == 1

    def test_get_all_events_filter_by_city(app_context):
        # Ví dụ city_id = 2 (Hà Nội/HCM tùy dữ liệu thật trong DB)
        events = get_all_events(city_id=2)
        for e in events.items:
            assert e.city_id == 2

    def test_get_all_events_filter_by_artist(app_context):
        # Ví dụ artist_id = 3
        events = get_all_events(artist_id=3)
        for e in events.items:
            # kiểm tra event có liên kết với artist_id=3
            artist_ids = [a.id for a in e.artists]
            assert 3 in artist_ids

    def test_get_all_events_filter_by_keyword(app_context):
        events = get_all_events(kw="Nhạc")
        for e in events.items:
            assert "Nhạc" in e.name

    def test_get_details_by_event_id(self):

        event_id = 1
        event_details = get_details_by_event_id(event_id)

        self.assertIsNotNone(event_details,"Event details không được None")

        self.assertIn("name", event_details)
        self.assertIn("time", event_details)
        self.assertIn("date", event_details)
        self.assertIn("type", event_details)
        self.assertIn("location", event_details)

    def test_create_event_with_tickets_success(self):
        # Chuẩn bị dữ liệu ticket
        ticket_data = {
            'prices': [100000, 200000],
            'quantities': [50, 30],
            'descriptions': ['Vé thường', 'Vé VIP'],
            'types': ['Standard', 'VIP']
        }

        new_event = create_event_with_tickets(
            name='Concert Test',
            city_id=1,
            district_id=1,
            address='123 Test Street',
            event_type_id=1,
            description='Mô tả sự kiện test',
            image_url='https://res.cloudinary.com/dfi68mgij/image/upload/v1756861793/6_imhqme.jpg',
            date='2025-09-13',
            time='18:00',
            organizer_id=1,
            ticket_data=ticket_data
        )

        # Kiểm tra event đã tạo
        self.assertIsNotNone(new_event.id)
        self.assertEqual(new_event.name, 'Concert Test')

        # Kiểm tra tickets đã tạo
        tickets = Ticket.query.filter_by(event_id=new_event.id).all()
        self.assertEqual(len(tickets), 2)

        # Kiểm tra ticket đầu tiên
        t1 = tickets[0]
        self.assertEqual(t1.price, 100000)
        self.assertEqual(t1.quantity, 50)
        self.assertEqual(t1.type, TypeTicket.Standard)
        self.assertEqual(t1.status, TicketStatus.Available)

        # Kiểm tra ticket thứ hai
        t2 = tickets[1]
        self.assertEqual(t2.type, TypeTicket.VIP)
        self.assertEqual(t2.price, 200000)

    def test_create_event_with_tickets_invalid_date(self):
        # Truyền sai format date => Exception
        ticket_data = {
            'prices': [100000],
            'quantities': [10],
            'descriptions': ['Vé thường'],
            'types': ['Standard']
        }

        with self.assertRaises(Exception):
            create_event_with_tickets(
                name='Concert Error',
                city_id=1,
                district_id=1,
                address='123 Test Street',
                event_type_id=1,
                description='Mô tả sự kiện test',
                image_url='https://res.cloudinary.com/dfi68mgij/image/upload/v1756861793/6_imhqme.jpg',
                date='13-09-2025',  # sai format
                time='18:00',
                organizer_id=1,
                ticket_data=ticket_data
            )

    def test_get_events_by_organizer_all(self):
            organizer = Organizer.query.first()
            pagination = get_events_by_organizer(organizer.id, page=1, per_page=5)

            # trả về phải là Pagination object
            assert hasattr(pagination, 'items')
            events = pagination.items

            assert all(e.organizer_id == organizer.id for e in events)
#Test lấy sự kiện sắp tới
    def test_get_events_by_organizer_upcoming(self):
            organizer = Organizer.query.first()
            pagination = get_events_by_organizer(organizer.id, page=1, per_page=5, status_filter='upcoming')
            events = pagination.items

            today = date.today()
            assert all(e.date > today for e in events)
#Test lấy sự kiện diễn ra
    def test_get_events_by_organizer_ongoing(seft):
            organizer = Organizer.query.first()
            pagination = get_events_by_organizer(organizer.id, status_filter='ongoing')
            events = pagination.items

            today = date.today()
            assert all(e.date == today for e in events)
#Test sự kiện đã qua
    def test_get_events_by_organizer_completed(seft):
            organizer = Organizer.query.first()
            pagination = get_events_by_organizer(organizer.id, status_filter='completed')
            events = pagination.items

            today = date.today()
            assert all(e.date < today for e in events)


if __name__=="__main__":
    unittest.main()