"""Unit tests for the VoiceMenu order engine."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import MenuItem, Order, OrderItem, Restaurant
from app.seed_menu import seed_database
from app.services.order_engine import (
    cancel_order,
    confirm_order,
    create_draft_order,
    generate_order_id,
    match_menu_items,
    update_draft_order,
    validate_order_item,
)


@pytest.fixture
def test_db():
    """In-memory SQLite database session fixture."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_seed_menu_populated(test_db):
    """Verify that demo restaurant and 15 items are correctly seeded."""
    restaurant = test_db.query(Restaurant).filter(Restaurant.id == "demo-restaurant").first()
    assert restaurant is not None
    assert restaurant.name == "South Spice Kitchen"

    items = test_db.query(MenuItem).filter(MenuItem.restaurant_id == "demo-restaurant").all()
    assert len(items) == 15

    # Check Chicken 65 is marked unavailable
    chicken_65 = next((i for i in items if i.id == "chicken-65"), None)
    assert chicken_65 is not None
    assert chicken_65.available is False


def test_match_menu_items(test_db):
    """Test fuzzy matching across canonical and localized names."""
    items = test_db.query(MenuItem).all()

    # Exact English
    matches = match_menu_items("Masala Dosa", items)
    assert len(matches) > 0
    assert matches[0][0].id == "masala-dosa"

    # Hindi match
    matches_hi = match_menu_items("मसाला डोसा", items)
    assert len(matches_hi) > 0
    assert matches_hi[0][0].id == "masala-dosa"

    # Fuzzy English
    matches_fuzzy = match_menu_items("filter cofi", items)
    assert len(matches_fuzzy) > 0
    assert matches_fuzzy[0][0].id == "filter-coffee"


def test_validate_order_item_success(test_db):
    """Test successful validation of an available item."""
    items = test_db.query(MenuItem).all()
    validated = validate_order_item(
        item_id="masala-dosa",
        quantity=2,
        customizations={"extra_spicy": "yes"},
        menu_items=items,
    )
    assert validated["menu_item_id"] == "masala-dosa"
    assert validated["quantity"] == 2
    assert validated["unit_price"] == 120.0
    assert validated["subtotal"] == 240.0


def test_validate_order_item_unavailable(test_db):
    """Test validation fails when item is out of stock."""
    items = test_db.query(MenuItem).all()
    with pytest.raises(ValueError, match="currently unavailable"):
        validate_order_item("chicken-65", 1, {}, items)


def test_validate_order_item_invalid_quantity(test_db):
    """Test validation fails when quantity is 0 or negative."""
    items = test_db.query(MenuItem).all()
    with pytest.raises(ValueError, match="greater than zero"):
        validate_order_item("masala-dosa", 0, {}, items)


def test_order_lifecycle(test_db):
    """Test full draft -> update -> confirm -> prevent duplicate flow."""
    # 1. Create draft order
    order = create_draft_order(
        restaurant_id="demo-restaurant",
        table_id="table-1",
        items=[
            {"menu_item_id": "masala-dosa", "quantity": 1},
            {"menu_item_id": "filter-coffee", "quantity": 2},
        ],
        language="en-IN",
        db=test_db,
    )
    assert order.id.startswith("SSK-")
    assert order.status == "pending"
    assert order.total_amount == 120.0 + (50.0 * 2)  # 220.0

    # 2. Update draft order
    updated = update_draft_order(
        order_id=order.id,
        items=[{"menu_item_id": "plain-dosa", "quantity": 2}],
        db=test_db,
    )
    assert updated.total_amount == 160.0
    assert len(updated.items) == 1
    assert updated.items[0].menu_item_id == "plain-dosa"

    # 3. Confirm order
    confirmed = confirm_order(order_id=order.id, db=test_db)
    assert confirmed.status == "accepted"

    # 4. Prevent duplicate confirmation
    with pytest.raises(ValueError, match="already been confirmed"):
        confirm_order(order_id=order.id, db=test_db)

    # 5. Prevent update on confirmed order
    with pytest.raises(ValueError, match="Only draft 'pending' orders can be updated"):
        update_draft_order(
            order_id=order.id,
            items=[{"menu_item_id": "masala-dosa", "quantity": 1}],
            db=test_db,
        )


def test_cancel_order(test_db):
    """Test cancelling an order."""
    order = create_draft_order(
        restaurant_id="demo-restaurant",
        table_id="table-2",
        items=[{"menu_item_id": "idli-sambar", "quantity": 1}],
        language="en-IN",
        db=test_db,
    )
    assert cancel_order(order.id, test_db) is True
    assert order.status == "cancelled"

    # Cannot cancel again
    with pytest.raises(ValueError, match="already cancelled"):
        cancel_order(order.id, test_db)
