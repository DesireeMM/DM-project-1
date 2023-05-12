import unittest

from server import app
from model import db, create_test_data, connect_to_db


class RouteTests(unittest.TestCase):
    """Tests for my web app."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        """Tests that homepage is displaying properly"""

        result = self.client.get("/")

        self.assertEqual(result.status_code, 200)
        self.assertIn(b'<a href="/new-account">Create New Account</a>', result.data)

    def test_not_logged_in(self):
        """Test that a user must be logged in to see dashboard"""

        result = self.client.get("/dashboard", follow_redirects=True)

        self.assertIn(b"You must log in to view your dashboard.", result.data)
        self.assertNotIn(b"<h1>Welcome John!</h1>", result.data)

class DatabaseTests(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'

        #Start each test with user1 logged in
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 1
                sess["logged_in_email"] = "john_doe@test.com"

        # Connect to test database (uncomment when testing database)
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data (uncomment when testing database)
        db.create_all()
        create_test_data()

    def tearDown(self):
        """Do at end of every test."""

        # (uncomment when testing database)
        db.drop_all()

    def test_login(self):
        """Test login route"""

        result = self.client.post("/login",
                                  data={"email": "john_doe@test.com",
                                        "password": "testing"},
                                  follow_redirects=True)

        self.assertNotIn(b"You must log in to view your dashboard.", result.data)
        self.assertIn(b"<h1>Welcome John!</h1>", result.data)

    def test_groups(self):
        """Test that groups display properly"""

        result = self.client.get("/groups", follow_redirects=True)
        self.assertIn(b"Sixers", result.data)

    def test_events(self):
        """Test that events display properly"""

        result = self.client.get("/events", follow_redirects=True)
        self.assertIn(b"Job Fair", result.data)


if __name__ == "__main__":
    unittest.main()