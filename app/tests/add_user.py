import unittest
from app import app, db
from app.models import User, Organizer, Role, ReviewStatus
from app.dao.user_dao import add_customer, add_organizer


class AddUser(unittest.TestCase):
    def setUp(self):
        # Tạo context Flask và reset database test
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()


    def test_add_customer(self):
        user = add_customer(
            username="test_customer",
            password="123456",
            email="customer@example.com",
            phone="0123456789"
        )

        # Kiểm tra user được thêm
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, "test_customer")
        self.assertEqual(user.role, Role.CUSTOMER)

        # Kiểm tra password đã được hash
        self.assertNotEqual(user.password, "123456")

    def test_add_organizer(self):
        user, organizer = add_organizer(
            username="test_organizer",
            password="654321",
            email="organizer@example.com",
            company_name="My Company",
            tax_code="TAX123",
            phone="0987654320"
        )

        # Kiểm tra user được thêm
        self.assertIsNotNone(user.id)
        self.assertEqual(user.role, Role.ORGANIZER)

        # Kiểm tra organizer liên kết với user
        self.assertIsNotNone(organizer.id)
        self.assertEqual(organizer.company_name, "My Company")
        self.assertEqual(organizer.tax_code, "TAX123")
        self.assertEqual(organizer.user_id, user.id)
        self.assertEqual(organizer.status, ReviewStatus.PENDING_APPROVAL)


if __name__=="__main__":
    unittest.main()