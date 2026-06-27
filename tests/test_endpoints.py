import unittest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.security import generate_qr_signature
from backend.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_hotel_management.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def seed_test_database():
    db = TestingSessionLocal()
    try:
        from backend.models.menu import MenuCategory, MenuItem
        if db.query(MenuCategory).count() == 0:
            cat = MenuCategory(cat_id="coffee", name="Coffee Items", description="Classics")
            db.add(cat)
            db.flush()
            db.add(MenuItem(name="Espresso", price=80.0, category_id=cat.id))
            db.commit()
    except Exception as e:
        print("Test seed failed:", e)
        db.rollback()
    finally:
        db.close()

class TestHotelManagementAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=test_engine)
        seed_test_database()
        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        app.dependency_overrides.clear()
        # Clean up test database file
        if os.path.exists("./test_hotel_management.db"):
            try:
                os.remove("./test_hotel_management.db")
            except Exception as e:
                print("Failed to delete test DB file:", e)

    def test_auth(self):
        # 1. Register a new user
        register_payload = {
            "username": "testwaiter",
            "password": "waiterpassword",
            "role": "waiter"
        }
        response = self.client.post("/api/auth/register", json=register_payload)
        self.assertIn(response.status_code, [201, 400])
        
        # 2. Login
        login_payload = {
            "username": "testwaiter",
            "password": "waiterpassword"
        }
        response = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "waiter")

    def test_menu(self):
        # Get public menu
        response = self.client.get("/api/menu")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("categories", data)

    def test_orders(self):
        import uuid
        # Place a table order with valid signature
        table_id = f"TEST-TBL-{uuid.uuid4().hex[:8]}"
        sig = generate_qr_signature(table_id)
        test_order_id = f"ORD-TEST-{uuid.uuid4().hex[:8]}"
        
        order_payload = {
            "order_id": test_order_id,
            "table_id": table_id,
            "sig": sig,
            "customer_phone": "7028952090",
            "status": "OPEN",
            "items": [
                {"name": "Espresso", "price": 80.0, "qty": 2}
            ]
        }
        
        response = self.client.post("/api/orders", json=order_payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["order_id"], test_order_id)
        self.assertEqual(data["table_id"], table_id)
        self.assertEqual(data["status"], "OPEN")

if __name__ == "__main__":
    unittest.main()
