"""Order management REST endpoints."""

import logging
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, Restaurant
from app.schemas import OrderCreateRequest, OrderResponse, OrderUpdateRequest
from app.services.order_engine import (
    cancel_order,
    confirm_order,
    create_draft_order,
    update_draft_order,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a draft order",
)
def create_order(
    payload: OrderCreateRequest,
    db: Session = Depends(get_db),
) -> OrderResponse:
    """Create a new draft order in 'pending' status.

    Args:
        payload (OrderCreateRequest): Order creation details including items.
        db (Session): Database session.

    Returns:
        OrderResponse: Created draft order.

    Raises:
        HTTPException: If restaurant is not found or item validation fails.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == payload.restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant '{payload.restaurant_id}' does not exist.",
        )

    try:
        items_data = [item.model_dump() for item in payload.items]
        order = create_draft_order(
            restaurant_id=payload.restaurant_id,
            table_id=payload.table_id,
            items=items_data,
            language=payload.language,
            db=db,
        )
        return OrderResponse.model_validate(order)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Get order details",
)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
) -> OrderResponse:
    """Fetch an order by its ID with line items.

    Args:
        order_id (str): Order identifier.
        db (Session): Database session.

    Returns:
        OrderResponse: Order details.

    Raises:
        HTTPException: If order is not found.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_id}' not found.",
        )
    return OrderResponse.model_validate(order)


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Update draft order items",
)
def update_order(
    order_id: str,
    payload: OrderUpdateRequest,
    db: Session = Depends(get_db),
) -> OrderResponse:
    """Replace line items in an existing draft order.

    Args:
        order_id (str): Target order ID.
        payload (OrderUpdateRequest): Replacement line items.
        db (Session): Database session.

    Returns:
        OrderResponse: Updated order.

    Raises:
        HTTPException: If order not found or not in draft state.
    """
    try:
        items_data = [item.model_dump() for item in payload.items]
        order = update_draft_order(order_id=order_id, items=items_data, db=db)
        return OrderResponse.model_validate(order)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{order_id}/confirm",
    response_model=OrderResponse,
    summary="Confirm order and send to kitchen",
)
def confirm_order_endpoint(
    order_id: str,
    db: Session = Depends(get_db),
) -> OrderResponse:
    """Confirm a draft order, revalidating prices and item availability.

    Prevents duplicate confirmations and transitions order status to 'accepted'.

    Args:
        order_id (str): ID of draft order.
        db (Session): Database session.

    Returns:
        OrderResponse: Confirmed order entity.

    Raises:
        HTTPException: If order not found, already confirmed, or item is out of stock.
    """
    try:
        order = confirm_order(order_id=order_id, db=db)
        return OrderResponse.model_validate(order)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/{order_id}",
    summary="Cancel order",
)
def cancel_order_endpoint(
    order_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Cancel a draft or active pending order.

    Args:
        order_id (str): Target order ID.
        db (Session): Database session.

    Returns:
        Dict[str, Any]: Cancellation confirmation.

    Raises:
        HTTPException: If order cannot be cancelled.
    """
    try:
        cancel_order(order_id=order_id, db=db)
        return {
            "success": True,
            "order_id": order_id,
            "message": f"Order '{order_id}' was successfully cancelled.",
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
