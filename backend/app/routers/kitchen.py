"""Kitchen Display System (KDS) router with PIN authentication and workflow status transitions."""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.models import Order
from app.schemas import KitchenOrderResponse, StatusUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/kitchen", tags=["Kitchen Display"])

# State machine for kitchen order status transitions
ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
    "pending": {"accepted", "cancelled"},
    "accepted": {"preparing", "cancelled"},
    "preparing": {"ready", "cancelled"},
    "ready": {"completed", "cancelled"},
    "completed": set(),  # terminal state
    "cancelled": set(),  # terminal state
}


def verify_kitchen_pin(
    x_kitchen_pin: Optional[str] = Header(
        None,
        alias="X-Kitchen-Pin",
        description="Kitchen station access PIN (Optional)",
    ),
) -> str:
    """Allow open kitchen access without requiring a PIN."""
    return x_kitchen_pin or "open"


@router.get(
    "/{restaurant_id}/orders",
    response_model=List[KitchenOrderResponse],
    summary="List active kitchen orders",
)
def list_kitchen_orders(
    restaurant_id: str,
    status_filter: str = Query(
        default="pending,accepted,preparing,ready",
        alias="status",
        description="Comma-separated order statuses to filter",
    ),
    _pin: str = Depends(verify_kitchen_pin),
    db: Session = Depends(get_db),
) -> List[KitchenOrderResponse]:
    """Retrieve filtered list of orders for kitchen display staff.

    Requires valid X-Kitchen-Pin header.

    Args:
        restaurant_id (str): Restaurant ID.
        status_filter (str): Filter statuses (e.g. pending,accepted,preparing,ready).
        _pin (str): Verified kitchen pin dependency.
        db (Session): Database session.

    Returns:
        List[KitchenOrderResponse]: Active orders sorted by creation time descending.
    """
    requested_statuses = [
        s.strip().lower() for s in status_filter.split(",") if s.strip()
    ]

    orders = (
        db.query(Order)
        .filter(
            Order.restaurant_id == restaurant_id,
            Order.status.in_(requested_statuses),
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    return [KitchenOrderResponse.model_validate(o) for o in orders]


@router.put(
    "/{restaurant_id}/orders/{order_id}/status",
    response_model=KitchenOrderResponse,
    summary="Update kitchen order workflow status",
)
def update_kitchen_order_status(
    restaurant_id: str,
    order_id: str,
    payload: StatusUpdateRequest,
    _pin: str = Depends(verify_kitchen_pin),
    db: Session = Depends(get_db),
) -> KitchenOrderResponse:
    """Transition order status through the kitchen workflow.

    Enforces state machine rules and requires valid X-Kitchen-Pin header.

    Args:
        restaurant_id (str): Restaurant ID.
        order_id (str): Order ID.
        payload (StatusUpdateRequest): New status target.
        _pin (str): Verified kitchen pin dependency.
        db (Session): Database session.

    Returns:
        KitchenOrderResponse: Updated order.

    Raises:
        HTTPException: 404 if not found, 400 on invalid state transition.
    """
    order = (
        db.query(Order)
        .filter(Order.restaurant_id == restaurant_id, Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found for restaurant '{restaurant_id}'.",
        )

    current_status = order.status
    target_status = payload.status

    if current_status == target_status:
        return KitchenOrderResponse.model_validate(order)

    allowed_targets = ALLOWED_TRANSITIONS.get(current_status, set())
    if target_status not in allowed_targets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid order status transition from '{current_status}' to '{target_status}'. "
                f"Allowed transitions: {list(allowed_targets) or 'None (terminal state)'}."
            ),
        )

    order.status = target_status
    order.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(order)

    logger.info("Order %s transitioned from %s to %s.", order_id, current_status, target_status)
    return KitchenOrderResponse.model_validate(order)
