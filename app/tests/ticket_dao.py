import unittest
from app import app, db
from app.models import Ticket,TypeTicket
from app.dao.ticket_dao import get_tickets_by_event_id


class TicketDaoTest(unittest.TestCase):
    def setUp(self):
        # Tạo context Flask và reset database test
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def test_get_tickets_by_event_id(self):
        # Giả sử trong DB test bạn biết chắc có event_id = 1
        event_id = 1

        tickets = get_tickets_by_event_id(event_id)

        # Kiểm tra danh sách tickets có đúng 2 loại
        self.assertEqual(len(tickets), 2, "Event id=1 phải có 2 loại ticket")

        # Tạo dict để dễ so sánh
        tickets_dict = {t.type: t.quantity for t in tickets}

        # So sánh từng loại vé
        self.assertEqual(
            tickets_dict.get(TypeTicket.Standard),
            100,
            "Ticket Standard phải có quantity = 100"
        )
        self.assertEqual(
            tickets_dict.get(TypeTicket.VIP),
            50,
            "Ticket VIP phải có quantity = 50"
        )


if __name__=="__main__":
    unittest.main()