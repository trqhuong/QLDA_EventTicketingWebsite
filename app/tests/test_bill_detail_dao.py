import unittest
from app import app
from app.dao import bill_detail_dao
from app.models import Bill_Detail, Bill, Ticket, Event, User, Role

class TestBillDetailDao(unittest.TestCase):
    def setUp(self):
        # Tạo test client, đảm bảo chạy trong app context
        self.app = app.test_client()

    def test_get_ticket_by_code_existing_ticket(self):
        """Test lấy vé theo mã code tồn tại"""
        with app.app_context():
            # Giả định có vé với code "TICKET001" trong database
            result = bill_detail_dao.get_ticket_by_code("TICKET001")
            if result:
                self.assertIsInstance(result, Bill_Detail)
                self.assertEqual(result.code, "TICKET001")

    def test_get_ticket_by_code_non_existing_ticket(self):
        """Test lấy vé theo mã code kh��ng tồn tại"""
        with app.app_context():
            result = bill_detail_dao.get_ticket_by_code("NONEXISTENT")
            self.assertIsNone(result)

    def test_get_ticket_by_code_empty_code(self):
        """Test lấy vé với mã code rỗng"""
        with app.app_context():
            result = bill_detail_dao.get_ticket_by_code("")
            self.assertIsNone(result)

            result = bill_detail_dao.get_ticket_by_code(None)
            self.assertIsNone(result)

    def test_mark_ticket_as_used_success(self):
        """Test đánh dấu vé đã sử dụng thành công"""
        with app.app_context():
            # Giả định có vé chưa sử dụng với code "TICKET001"
            result = bill_detail_dao.mark_ticket_as_used("TICKET001")
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
            self.assertIn('message', result)
            self.assertIn('type', result)

    def test_mark_ticket_as_used_already_used(self):
        """Test đánh dấu vé đã được sử dụng"""
        with app.app_context():
            # Đầu tiên đánh dấu vé đã sử dụng
            bill_detail_dao.mark_ticket_as_used("TICKET001")

            # Sau đó thử đánh dấu lại
            result = bill_detail_dao.mark_ticket_as_used("TICKET001")
            self.assertIsInstance(result, dict)
            self.assertFalse(result.get('success'))
            self.assertEqual(result.get('type'), 'warning')
            self.assertIn('đã được sử dụng', result.get('message', ''))

    def test_mark_ticket_as_used_non_existing_ticket(self):
        """Test đánh dấu vé không tồn tại"""
        with app.app_context():
            result = bill_detail_dao.mark_ticket_as_used("NONEXISTENT")
            self.assertIsInstance(result, dict)
            self.assertFalse(result.get('success'))
            self.assertEqual(result.get('type'), 'error')
            self.assertIn('Không tìm thấy vé', result.get('message', ''))

    def test_mark_ticket_as_used_empty_code(self):
        """Test đánh dấu vé với mã code rỗng"""
        with app.app_context():
            result = bill_detail_dao.mark_ticket_as_used("")
            self.assertIsInstance(result, dict)
            self.assertFalse(result.get('success'))

            result = bill_detail_dao.mark_ticket_as_used(None)
            self.assertIsInstance(result, dict)
            self.assertFalse(result.get('success'))

    def test_get_ticket_by_code_return_structure(self):
        """Test cấu trúc dữ liệu trả về của get_ticket_by_code"""
        with app.app_context():
            result = bill_detail_dao.get_ticket_by_code("TICKET001")
            if result:
                # Kiểm tra các thuộc tính cần thiết
                self.assertTrue(hasattr(result, 'code'))
                self.assertTrue(hasattr(result, 'used'))
                self.assertTrue(hasattr(result, 'bought_quantity'))
                self.assertTrue(hasattr(result, 'bill'))
                self.assertTrue(hasattr(result, 'ticket'))

    def test_mark_ticket_return_structure(self):
        """Test cấu trúc dữ liệu trả về của mark_ticket_as_used"""
        with app.app_context():
            result = bill_detail_dao.mark_ticket_as_used("TICKET001")

            # Kiểm tra cấu trúc response
            self.assertIsInstance(result, dict)
            required_keys = ['success', 'message', 'type']
            for key in required_keys:
                self.assertIn(key, result)

            # Kiểm tra kiểu dữ liệu
            self.assertIsInstance(result['success'], bool)
            self.assertIsInstance(result['message'], str)
            self.assertIsInstance(result['type'], str)

            # Kiểm tra giá trị type hợp lệ
            valid_types = ['success', 'warning', 'error']
            self.assertIn(result['type'], valid_types)

if __name__ == "__main__":
    unittest.main()
