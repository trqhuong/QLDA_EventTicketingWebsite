import unittest
from app import app
from app.dao import user_dao
from app.models import Role

class TestLogin(unittest.TestCase):
    def setUp(self):
        # Tạo test client, đảm bảo chạy trong app context
        self.app = app.test_client()

    def test_auth_user_correct(self):
        with app.app_context():
            user = user_dao.auth_user("huong", "123")
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "huong")

    def test_auth_user_wrong_password(self):
        with app.app_context():
            user = user_dao.auth_user("huong", "345")
            self.assertIsNone(user)

    def test_auth_user_with_role(self):
        with app.app_context():
            user = user_dao.auth_user("huong", "123", role="ADMIN")
            self.assertIsNotNone(user)
            self.assertEqual(user.role, Role.ADMIN)

    def test_auth_user_wrong_role(self):
        with app.app_context():
            user = user_dao.auth_user("han312", "123", role="ADMIN")
            self.assertIsNone(user)

if __name__=="__main__":
    unittest.main()