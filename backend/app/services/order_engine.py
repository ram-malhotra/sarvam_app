"""Order processing engine for VoiceMenu AI."""

import difflib
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlalchemy.orm import Session
from app.models import MenuItem, Order, OrderItem, Restaurant

logger = logging.getLogger(__name__)


def generate_order_id(restaurant_id: str, db: Session) -> str:
    """Generate a readable, sequential order ID such as 'SSK-20261026-001'.

    Args:
        restaurant_id (str): ID of the restaurant.
        db (Session): SQLAlchemy database session.

    Returns:
        str: Formatted unique order ID.
    """
    # Derive prefix from restaurant initials or default
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if restaurant and restaurant.name:
        words = restaurant.name.split()
        prefix = "".join(w[0].upper() for w in words if w)
        if len(prefix) < 2:
            prefix = prefix.ljust(3, "X")
    else:
        prefix = "VM"

    date_str = datetime.utcnow().strftime("%Y%m%d")
    id_pattern = f"{prefix}-{date_str}-"

    # Count today's orders for sequence numbering
    existing_today_count = (
        db.query(Order)
        .filter(Order.id.like(f"{id_pattern}%"))
        .count()
    )

    sequence_num = existing_today_count + 1
    order_id = f"{id_pattern}{sequence_num:03d}"

    # Ensure uniqueness in case of race or concurrent creations
    while db.query(Order).filter(Order.id == order_id).first() is not None:
        sequence_num += 1
        order_id = f"{id_pattern}{sequence_num:03d}"

    return order_id


def match_menu_items(query: str, menu_items: List[MenuItem]) -> List[Tuple[MenuItem, float]]:
    """Fuzzy match user query string against menu item names in canonical and localized languages.

    Args:
        query (str): Search term or voice transcript.
        menu_items (List[MenuItem]): List of candidate menu items.

    Returns:
        List[Tuple[MenuItem, float]]: List of (item, confidence_score) sorted descending by score.
    """
    clean_query = query.strip().lower()
    if not clean_query:
        return []

    scored_items: List[Tuple[MenuItem, float]] = []

    for item in menu_items:
        best_score = 0.0

        # Candidate names to test
        candidates = [item.canonical_name.lower(), item.id.lower(), item.category.lower()]
        if isinstance(item.localized_names, dict):
            for loc_name in item.localized_names.values():
                if loc_name:
                    candidates.append(loc_name.lower())

        for cand in candidates:
            if clean_query == cand:
                best_score = max(best_score, 1.0)
            elif cand in clean_query or clean_query in cand:
                best_score = max(best_score, 0.85)
            else:
                ratio = difflib.SequenceMatcher(None, clean_query, cand).ratio()
                best_score = max(best_score, ratio)

        if best_score >= 0.45:
            scored_items.append((item, round(best_score, 3)))

    scored_items.sort(key=lambda x: x[1], reverse=True)
    return scored_items


def validate_order_item(
    item_id: str,
    quantity: int,
    customizations: Optional[Dict[str, Any]],
    menu_items: List[MenuItem],
) -> Dict[str, Any]:
    """Validate menu item existence, stock availability, quantity, and customizations.

    Args:
        item_id (str): Identifier of the menu item.
        quantity (int): Number of portions requested.
        customizations (Optional[Dict[str, Any]]): User options (e.g. extra_spicy=yes).
        menu_items (List[MenuItem]): Active menu items list.

    Returns:
        Dict[str, Any]: Validated item payload with pricing.

    Raises:
        ValueError: If item does not exist, is unavailable, or quantity is non-positive.
    """
    if quantity <= 0:
        raise ValueError(f"Quantity must be greater than zero, received {quantity}.")

    matched_item = next((m for m in menu_items if m.id == item_id), None)
    if not matched_item:
        raise ValueError(f"Menu item '{item_id}' not found.")

    if not matched_item.available:
        raise ValueError(f"'{matched_item.canonical_name}' is currently unavailable.")

    clean_customizations = customizations or {}
    unit_price = round(float(matched_item.price), 2)
    subtotal = round(unit_price * quantity, 2)

    return {
        "menu_item_id": matched_item.id,
        "item_name": matched_item.canonical_name,
        "quantity": quantity,
        "customizations": clean_customizations,
        "unit_price": unit_price,
        "subtotal": subtotal,
    }


def calculate_order_total(items: Union[List[OrderItem], List[Dict[str, Any]]]) -> float:
    """Calculate the total price of an order from line items.

    Args:
        items (Union[List[OrderItem], List[Dict[str, Any]]]): List of order items or item dicts.

    Returns:
        float: Rounded total amount.
    """
    total = 0.0
    for item in items:
        if isinstance(item, OrderItem):
            total += float(item.subtotal)
        elif isinstance(item, dict):
            subtotal = item.get("subtotal")
            if subtotal is not None:
                total += float(subtotal)
            else:
                unit = float(item.get("unit_price", 0.0))
                qty = int(item.get("quantity", 1))
                total += unit * qty
        else:
            subtotal = getattr(item, "subtotal", 0.0)
            total += float(subtotal)

    return round(total, 2)


def create_draft_order(
    restaurant_id: str,
    table_id: str,
    items: List[Dict[str, Any]],
    language: str,
    db: Session,
) -> Order:
    """Create a new draft order in 'pending' status.

    Args:
        restaurant_id (str): Restaurant ID.
        table_id (str): Table number or code.
        items (List[Dict[str, Any]]): Requested line items.
        language (str): Ordering language (e.g. en-IN).
        db (Session): Database session.

    Returns:
        Order: The newly created Order entity.
    """
    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == restaurant_id)
        .all()
    )

    validated_lines: List[Dict[str, Any]] = []
    for line in items:
        item_id = line.get("menu_item_id") or line.get("item_id")
        qty = int(line.get("quantity", 1))
        customizations = line.get("customizations", {})
        val = validate_order_item(item_id, qty, customizations, menu_items)
        validated_lines.append(val)

    total_amount = calculate_order_total(validated_lines)
    order_id = generate_order_id(restaurant_id, db)

    order = Order(
        id=order_id,
        restaurant_id=restaurant_id,
        table_id=table_id,
        status="pending",
        total_amount=total_amount,
        language=language,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(order)
    db.flush()

    for line in validated_lines:
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=line["menu_item_id"],
            item_name=line["item_name"],
            quantity=line["quantity"],
            customizations=line["customizations"],
            unit_price=line["unit_price"],
            subtotal=line["subtotal"],
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)
    return order


def update_draft_order(order_id: str, items: List[Dict[str, Any]], db: Session) -> Order:
    """Update line items for an existing draft order.

    Args:
        order_id (str): Target order ID.
        items (List[Dict[str, Any]]): Updated list of line items.
        db (Session): Database session.

    Returns:
        Order: The updated Order entity.

    Raises:
        ValueError: If order does not exist or has already transitioned past draft state.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError(f"Order '{order_id}' not found.")

    if order.status != "pending":
        raise ValueError(
            f"Cannot update order '{order_id}' with status '{order.status}'. Only draft 'pending' orders can be updated."
        )

    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == order.restaurant_id)
        .all()
    )

    validated_lines: List[Dict[str, Any]] = []
    for line in items:
        item_id = line.get("menu_item_id") or line.get("item_id")
        qty = int(line.get("quantity", 1))
        customizations = line.get("customizations", {})
        val = validate_order_item(item_id, qty, customizations, menu_items)
        validated_lines.append(val)

    # Remove existing items
    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()

    # Re-add updated items
    for line in validated_lines:
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=line["menu_item_id"],
            item_name=line["item_name"],
            quantity=line["quantity"],
            customizations=line["customizations"],
            unit_price=line["unit_price"],
            subtotal=line["subtotal"],
        )
        db.add(order_item)

    order.total_amount = calculate_order_total(validated_lines)
    order.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(order)
    return order


def confirm_order(order_id: str, db: Session) -> Order:
    """Confirm a draft order after revalidating current prices and stock availability.

    Prevents duplicate confirmations and invalid status transitions.

    Args:
        order_id (str): ID of the order to confirm.
        db (Session): Database session.

    Returns:
        Order: The confirmed Order entity in 'accepted' status.

    Raises:
        ValueError: If order cannot be confirmed or item availability failed.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError(f"Order '{order_id}' not found.")

    if order.status in ["accepted", "preparing", "ready", "completed"]:
        raise ValueError(f"Order '{order_id}' has already been confirmed (status: '{order.status}').")

    if order.status == "cancelled":
        raise ValueError(f"Order '{order_id}' is cancelled and cannot be confirmed.")

    if order.status != "pending":
        raise ValueError(f"Order '{order_id}' cannot transition from '{order.status}' to 'accepted'.")

    if not order.items:
        raise ValueError(f"Order '{order_id}' has no items and cannot be confirmed.")

    # Fetch latest menu state for revalidation
    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == order.restaurant_id)
        .all()
    )
    menu_map = {m.id: m for m in menu_items}

    # Revalidate availability & prices
    for item in order.items:
        current_menu_item = menu_map.get(item.menu_item_id)
        if not current_menu_item:
            raise ValueError(f"Item '{item.item_name}' (ID: {item.menu_item_id}) no longer exists in menu.")
        if not current_menu_item.available:
            raise ValueError(f"Item '{item.item_name}' is currently sold out and cannot be ordered.")

        # Update price if changed in menu
        item.unit_price = round(float(current_menu_item.price), 2)
        item.subtotal = round(item.unit_price * item.quantity, 2)

    order.total_amount = calculate_order_total(order.items)
    order.status = "accepted"
    order.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(order)
    return order


def cancel_order(order_id: str, db: Session) -> bool:
    """Cancel an order if it is in an eligible non-terminal state.

    Args:
        order_id (str): Order ID to cancel.
        db (Session): Database session.

    Returns:
        bool: True if cancellation succeeded.

    Raises:
        ValueError: If order not found or already completed/cancelled.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError(f"Order '{order_id}' not found.")

    if order.status in ["ready", "completed"]:
        raise ValueError(f"Cannot cancel order '{order_id}' because it is already {order.status}.")

    if order.status == "cancelled":
        raise ValueError(f"Order '{order_id}' is already cancelled.")

    order.status = "cancelled"
    order.updated_at = datetime.utcnow()
    db.commit()
    return True
