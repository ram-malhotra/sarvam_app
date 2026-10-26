"""Integration tests for VoiceMenu AI FastAPI routes."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.seed_menu import seed_database

# Setup test in-memory SQLite database with StaticPool so all connections share the same memory DB
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)

# Seed test database once
with TestingSessionLocal() as session:
    seed_database(session)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_health_check():
    """Verify health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "voicemenu-backend"


def test_get_restaurant():
    """Verify restaurant retrieval endpoint."""
    response = client.get("/api/restaurants/demo-restaurant")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "demo-restaurant"
    assert data["name"] == "South Spice Kitchen"


def test_get_menu_filtering():
    """Verify menu filtering by category and veg status."""
    # All items
    response = client.get("/api/restaurants/demo-restaurant/menu")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 15
    assert "dosa" in data["categories"]

    # Dosa category only
    response_dosa = client.get("/api/restaurants/demo-restaurant/menu?category=dosa")
    assert response_dosa.status_code == 200
    assert len(response_dosa.json()["items"]) == 4

    # Veg only
    response_veg = client.get("/api/restaurants/demo-restaurant/menu?veg_only=true")
    assert response_veg.status_code == 200
    assert all(i["is_veg"] is True for i in response_veg.json()["items"])


def test_get_menu_item_detail():
    """Verify single menu item endpoint."""
    response = client.get("/api/restaurants/demo-restaurant/menu/masala-dosa")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "masala-dosa"
    assert data["price"] == 120.0
    assert data["available"] is True


def test_order_flow_api():
    """Verify order creation, confirmation, and kitchen retrieval via API."""
    # 1. Create draft order
    create_payload = {
        "restaurant_id": "demo-restaurant",
        "table_id": "T1",
        "language": "en-IN",
        "items": [
            {"menu_item_id": "masala-dosa", "quantity": 1, "customizations": {}},
            {"menu_item_id": "filter-coffee", "quantity": 1, "customizations": {}},
        ],
    }
    response = client.post("/api/orders", json=create_payload)
    assert response.status_code == 201
    order_data = response.json()
    order_id = order_data["id"]
    assert order_data["status"] == "pending"
    assert order_data["total_amount"] == 170.0

    # 2. Get order
    get_res = client.get(f"/api/orders/{order_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == order_id

    # 3. Confirm order
    confirm_res = client.post(f"/api/orders/{order_id}/confirm")
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "accepted"

    # 4. Kitchen orders unauthorized check
    kitchen_unauth = client.get("/api/kitchen/demo-restaurant/orders")
    assert kitchen_unauth.status_code == 401

    # 5. Kitchen orders authorized check
    kitchen_auth = client.get(
        "/api/kitchen/demo-restaurant/orders",
        headers={"X-Kitchen-Pin": "1234"},
    )
    assert kitchen_auth.status_code == 200
    orders_list = kitchen_auth.json()
    assert any(o["id"] == order_id for o in orders_list)

    # 6. Kitchen updates status to preparing
    status_update = client.put(
        f"/api/kitchen/demo-restaurant/orders/{order_id}/status",
        headers={"X-Kitchen-Pin": "1234"},
        json={"status": "preparing"},
    )
    assert status_update.status_code == 200
    assert status_update.json()["status"] == "preparing"


def test_qr_code_generation():
    """Verify QR code PNG generation."""
    response = client.get("/api/qr/demo-restaurant/table-4?base_url=http://localhost:5173")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 100  # PNG image bytes


def test_voice_converse_api():
    """Verify conversational endpoint responds with cart update."""
    payload = {
        "text": "Please add two masala dosa to my order",
        "language": "en-IN",
        "restaurant_id": "demo-restaurant",
        "table_id": "T4",
        "conversation_history": [],
        "current_cart": [],
    }
    response = client.post("/api/voice/converse", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response_text" in data
    assert len(data["current_cart"]) == 1
    assert data["current_cart"][0]["item_id"] == "masala-dosa"
    assert data["current_cart"][0]["quantity"] == 2
