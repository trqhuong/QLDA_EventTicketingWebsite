import unittest
from unittest.mock import patch, MagicMock
from app import app
from app.dao import bill_dao
from app.models import Event, Bill, Bill_Detail, Ticket, Organizer, User
from datetime import datetime

class TestBillDao(unittest.TestCase):
    def setUp(self):
        # Tạo test client, đảm bảo chạy trong app context
        self.app = app.test_client()
        self.organizer_id = 1
        self.year = 2024
        self.user_id = 1
        self.month = 12
        self.quarter = 4

    def test_get_report_data_with_year(self):
        """Test lấy dữ liệu thống kê theo năm"""
        with app.app_context():
            result = bill_dao.get_report_data(self.organizer_id, year=self.year)
            self.assertIsInstance(result, dict)
            self.assertIn('total_events', result)
            self.assertIn('total_revenue', result)
            self.assertIsInstance(result['total_events'], int)
            self.assertIsInstance(result['total_revenue'], (int, float))

    def test_get_report_data_with_month(self):
        """Test lấy dữ liệu thống kê theo tháng"""
        with app.app_context():
            result = bill_dao.get_report_data(self.organizer_id, year=self.year, month=self.month)
            self.assertIsInstance(result, dict)
            self.assertIn('total_events', result)
            self.assertIn('total_revenue', result)

    def test_get_report_data_with_quarter(self):
        """Test lấy dữ liệu thống kê theo quý"""
        with app.app_context():
            result = bill_dao.get_report_data(self.organizer_id, year=self.year, quarter=self.quarter)
            self.assertIsInstance(result, dict)
            self.assertIn('total_events', result)
            self.assertIn('total_revenue', result)

    def test_get_quarter_months(self):
        """Test lấy danh sách tháng theo quý"""
        with app.app_context():
            # Test quý 1
            result = bill_dao.get_quarter_months(1)
            self.assertEqual(result, [1, 2, 3])

            # Test quý 2
            result = bill_dao.get_quarter_months(2)
            self.assertEqual(result, [4, 5, 6])

            # Test quý 3
            result = bill_dao.get_quarter_months(3)
            self.assertEqual(result, [7, 8, 9])

            # Test quý 4
            result = bill_dao.get_quarter_months(4)
            self.assertEqual(result, [10, 11, 12])

            # Test quý không hợp lệ
            result = bill_dao.get_quarter_months(5)
            self.assertEqual(result, [])

    def test_get_monthly_events_data_all_months(self):
        """Test lấy dữ liệu sự kiện theo 12 tháng"""
        with app.app_context():
            result = bill_dao.get_monthly_events_data(self.organizer_id, year=self.year)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 12)
            for count in result:
                self.assertIsInstance(count, int)

    def test_get_monthly_events_data_single_month(self):
        """Test lấy dữ liệu sự kiện theo tháng cụ thể"""
        with app.app_context():
            result = bill_dao.get_monthly_events_data(self.organizer_id, year=self.year, month=self.month)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], int)

    def test_get_monthly_events_data_quarter(self):
        """Test lấy dữ liệu sự kiện theo quý"""
        with app.app_context():
            result = bill_dao.get_monthly_events_data(self.organizer_id, year=self.year, quarter=self.quarter)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 3)
            for count in result:
                self.assertIsInstance(count, int)

    def test_get_monthly_revenue_data_all_months(self):
        """Test lấy dữ liệu doanh thu theo 12 tháng"""
        with app.app_context():
            result = bill_dao.get_monthly_revenue_data(self.organizer_id, year=self.year)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 12)
            for revenue in result:
                self.assertIsInstance(revenue, (int, float))

    def test_get_monthly_revenue_data_single_month(self):
        """Test lấy dữ liệu doanh thu theo tháng cụ thể"""
        with app.app_context():
            result = bill_dao.get_monthly_revenue_data(self.organizer_id, year=self.year, month=self.month)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], (int, float))

    def test_get_monthly_revenue_data_quarter(self):
        """Test lấy dữ liệu doanh thu theo quý"""
        with app.app_context():
            result = bill_dao.get_monthly_revenue_data(self.organizer_id, year=self.year, quarter=self.quarter)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 3)
            for revenue in result:
                self.assertIsInstance(revenue, (int, float))

    def test_get_available_years(self):
        """Test lấy danh sách năm có sự kiện"""
        with app.app_context():
            result = bill_dao.get_available_years(self.organizer_id)
            self.assertIsInstance(result, list)
            for year in result:
                self.assertIsInstance(year, int)

    def test_get_event_statistics(self):
        """Test lấy thống kê chi tiết sự kiện"""
        with app.app_context():
            result = bill_dao.get_event_statistics(self.organizer_id, year=self.year)
            self.assertIsInstance(result, list)
            # Kiểm tra structure của từng event trong result
            for event in result:
                self.assertTrue(hasattr(event, 'id'))
                self.assertTrue(hasattr(event, 'name'))
                self.assertTrue(hasattr(event, 'date'))
                self.assertTrue(hasattr(event, 'time'))
                self.assertTrue(hasattr(event, 'tickets_sold'))
                self.assertTrue(hasattr(event, 'revenue'))

    # ============ ADMIN FUNCTIONS TESTS ============

    def test_get_admin_report_data_with_year(self):
        """Test lấy dữ liệu thống kê admin theo năm"""
        with app.app_context():
            result = bill_dao.get_admin_report_data(year=self.year)
            self.assertIsInstance(result, dict)
            self.assertIn('total_events', result)
            self.assertIn('total_revenue', result)
            self.assertIsInstance(result['total_events'], int)
            self.assertIsInstance(result['total_revenue'], (int, float))

    def test_get_admin_report_data_with_month(self):
        """Test lấy dữ liệu thống kê admin theo tháng"""
        with app.app_context():
            result = bill_dao.get_admin_report_data(year=self.year, month=self.month)
            self.assertIsInstance(result, dict)
            self.assertIn('total_events', result)
            self.assertIn('total_revenue', result)

    def test_get_admin_report_data_with_quarter(self):
        """Test lấy dữ liệu thống kê admin theo quý"""
        with app.app_context():
            result = bill_dao.get_admin_report_data(year=self.year, quarter=self.quarter)
            self.assertIsInstance(result, dict)
            self.assertIn('total_events', result)
            self.assertIn('total_revenue', result)

    def test_get_admin_monthly_events_data_all_months(self):
        """Test lấy dữ liệu sự kiện admin theo 12 tháng"""
        with app.app_context():
            result = bill_dao.get_admin_monthly_events_data(year=self.year)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 12)
            for count in result:
                self.assertIsInstance(count, int)

    def test_get_admin_monthly_events_data_single_month(self):
        """Test lấy dữ liệu sự kiện admin theo tháng cụ thể"""
        with app.app_context():
            result = bill_dao.get_admin_monthly_events_data(year=self.year, month=self.month)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], int)

    def test_get_admin_monthly_events_data_quarter(self):
        """Test lấy dữ liệu sự kiện admin theo quý"""
        with app.app_context():
            result = bill_dao.get_admin_monthly_events_data(year=self.year, quarter=self.quarter)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 3)
            for count in result:
                self.assertIsInstance(count, int)

    def test_get_admin_monthly_revenue_data_all_months(self):
        """Test lấy dữ liệu doanh thu admin theo 12 tháng"""
        with app.app_context():
            result = bill_dao.get_admin_monthly_revenue_data(year=self.year)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 12)
            for revenue in result:
                self.assertIsInstance(revenue, (int, float))

    def test_get_admin_monthly_revenue_data_single_month(self):
        """Test lấy dữ liệu doanh thu admin theo tháng cụ thể"""
        with app.app_context():
            result = bill_dao.get_admin_monthly_revenue_data(year=self.year, month=self.month)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], (int, float))

    def test_get_admin_monthly_revenue_data_quarter(self):
        """Test lấy dữ liệu doanh thu admin theo quý"""
        with app.app_context():
            result = bill_dao.get_admin_monthly_revenue_data(year=self.year, quarter=self.quarter)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 3)
            for revenue in result:
                self.assertIsInstance(revenue, (int, float))

    def test_get_admin_available_years(self):
        """Test lấy danh sách năm có sự kiện trong toàn hệ thống"""
        with app.app_context():
            result = bill_dao.get_admin_available_years()
            self.assertIsInstance(result, list)
            for year in result:
                self.assertIsInstance(year, int)

    def test_get_admin_event_statistics(self):
        """Test lấy thống kê chi tiết sự kiện admin"""
        with app.app_context():
            result = bill_dao.get_admin_event_statistics(year=self.year)
            self.assertIsInstance(result, list)
            # Kiểm tra structure của từng event trong result
            for event in result:
                self.assertTrue(hasattr(event, 'id'))
                self.assertTrue(hasattr(event, 'name'))
                self.assertTrue(hasattr(event, 'date'))
                self.assertTrue(hasattr(event, 'time'))
                self.assertTrue(hasattr(event, 'company_name'))
                self.assertTrue(hasattr(event, 'tickets_sold'))
                self.assertTrue(hasattr(event, 'revenue'))

    # ============ USER TICKETS TESTS ============

    def test_get_user_tickets(self):
        """Test lấy danh sách vé của người dùng"""
        with app.app_context():
            result = bill_dao.get_user_tickets(self.user_id)
            self.assertIsInstance(result, list)
            # Kiểm tra structure của từng ticket trong result
            for ticket in result:
                self.assertTrue(hasattr(ticket, 'bill_detail_id'))
                self.assertTrue(hasattr(ticket, 'bought_quantity'))
                self.assertTrue(hasattr(ticket, 'code'))
                self.assertTrue(hasattr(ticket, 'used'))
                self.assertTrue(hasattr(ticket, 'bill_id'))
                self.assertTrue(hasattr(ticket, 'status_ticket'))
                self.assertTrue(hasattr(ticket, 'created_date'))
                self.assertTrue(hasattr(ticket, 'total_price'))
                self.assertTrue(hasattr(ticket, 'ticket_type'))
                self.assertTrue(hasattr(ticket, 'ticket_price'))
                self.assertTrue(hasattr(ticket, 'event_name'))
                self.assertTrue(hasattr(ticket, 'event_date'))
                self.assertTrue(hasattr(ticket, 'event_time'))
                self.assertTrue(hasattr(ticket, 'event_address'))
                self.assertTrue(hasattr(ticket, 'event_image'))

    def test_get_user_tickets_with_pagination(self):
        """Test lấy danh sách vé của người dùng với phân trang"""
        with app.app_context():
            page = 1
            per_page = 5
            result = bill_dao.get_user_tickets_with_pagination(self.user_id, page=page, per_page=per_page)

            # Kiểm tra pagination object
            self.assertTrue(hasattr(result, 'items'))
            self.assertTrue(hasattr(result, 'page'))
            self.assertTrue(hasattr(result, 'per_page'))
            self.assertTrue(hasattr(result, 'total'))
            self.assertTrue(hasattr(result, 'pages'))
            self.assertTrue(hasattr(result, 'has_prev'))
            self.assertTrue(hasattr(result, 'has_next'))

            self.assertEqual(result.page, page)
            self.assertEqual(result.per_page, per_page)
            self.assertIsInstance(result.items, list)

            # Kiểm tra structure của từng ticket trong items
            for ticket in result.items:
                self.assertTrue(hasattr(ticket, 'bill_detail_id'))
                self.assertTrue(hasattr(ticket, 'bought_quantity'))
                self.assertTrue(hasattr(ticket, 'code'))
                self.assertTrue(hasattr(ticket, 'used'))
                self.assertTrue(hasattr(ticket, 'event_name'))

    def test_get_user_tickets_with_pagination_different_page(self):
        """Test phân trang với page khác nhau"""
        with app.app_context():
            # Test page 1
            result_page1 = bill_dao.get_user_tickets_with_pagination(self.user_id, page=1, per_page=2)
            self.assertEqual(result_page1.page, 1)

            # Test page 2 nếu có dữ liệu
            result_page2 = bill_dao.get_user_tickets_with_pagination(self.user_id, page=2, per_page=2)
            self.assertEqual(result_page2.page, 2)

    def test_edge_cases(self):
        """Test các trường hợp biên"""
        with app.app_context():
            # Test với organizer_id không tồn tại
            result = bill_dao.get_report_data(9999, year=self.year)
            self.assertEqual(result['total_events'], 0)
            self.assertEqual(result['total_revenue'], 0)

            # Test với user_id không tồn tại
            result = bill_dao.get_user_tickets(9999)
            self.assertEqual(len(result), 0)

            # Test với year không có dữ liệu
            result = bill_dao.get_available_years(9999)
            self.assertEqual(len(result), 0)

if __name__ == "__main__":
    unittest.main()
