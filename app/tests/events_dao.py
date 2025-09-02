import unittest
from app import app, db
from app.models import User, Organizer, Role, ReviewStatus
from app.dao.events_dao import get_all_events


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

if __name__=="__main__":
    unittest.main()