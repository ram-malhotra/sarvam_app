"""Menu and restaurant REST endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import MenuItem, Restaurant
from app.schemas import MenuItemResponse, MenuResponse, RestaurantResponse
from app.services.sarvam_translate import translate_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/restaurants", tags=["Menu & Restaurants"])


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantResponse,
    summary="Get restaurant details",
)
def get_restaurant(
    restaurant_id: str,
    db: Session = Depends(get_db),
) -> RestaurantResponse:
    """Retrieve details for a specific restaurant by its unique ID.

    Args:
        restaurant_id (str): Restaurant identifier (e.g. 'demo-restaurant').
        db (Session): Database session.

    Returns:
        RestaurantResponse: Restaurant metadata.

    Raises:
        HTTPException: If restaurant is not found.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant '{restaurant_id}' not found.",
        )
    return RestaurantResponse.model_validate(restaurant)


@router.get(
    "/{restaurant_id}/menu",
    response_model=MenuResponse,
    summary="Get localized restaurant menu",
)
async def get_menu(
    restaurant_id: str,
    language: str = Query(default="en-IN", description="Language code (en-IN, hi-IN, ta-IN, te-IN)"),
    category: Optional[str] = Query(default=None, description="Filter items by category"),
    veg_only: bool = Query(default=False, description="Filter for vegetarian items only"),
    db: Session = Depends(get_db),
) -> MenuResponse:
    """Retrieve catalog items for a restaurant with localized names and descriptions.

    Args:
        restaurant_id (str): Target restaurant ID.
        language (str): Client interface language.
        category (Optional[str]): Category slug or name filter.
        veg_only (bool): If True, filters out non-vegetarian dishes.
        db (Session): Database session.

    Returns:
        MenuResponse: List of filtered and localized menu items.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant '{restaurant_id}' not found.",
        )

    # Fetch available categories for restaurant
    categories_query = (
        db.query(MenuItem.category)
        .filter(MenuItem.restaurant_id == restaurant_id)
        .distinct()
        .all()
    )
    categories = [cat[0] for cat in categories_query if cat[0]]

    # Query menu items
    query = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id)

    if category:
        query = query.filter(MenuItem.category == category.lower().strip())
    if veg_only:
        query = query.filter(MenuItem.is_veg == True)  # noqa: E712

    menu_items = query.all()

    response_items: List[MenuItemResponse] = []
    for item in menu_items:
        # Determine localized display name
        display_name = item.canonical_name
        if language != "en-IN" and isinstance(item.localized_names, dict):
            display_name = item.localized_names.get(language) or item.canonical_name

        # Determine localized description
        display_description = item.description
        if language != "en-IN":
            loc_descs = item.localized_descriptions if isinstance(item.localized_descriptions, dict) else {}
            if language in loc_descs:
                display_description = loc_descs[language]
            else:
                # Dynamic translation with cache
                try:
                    display_description = await translate_text(
                        text=item.description,
                        source_lang="en-IN",
                        target_lang=language,
                        db=db,
                    )
                except Exception as exc:
                    logger.warning("Dynamic translation fallback for %s: %s", item.id, exc)
                    display_description = item.description

        item_dto = MenuItemResponse(
            id=item.id,
            restaurant_id=item.restaurant_id,
            category=item.category,
            canonical_name=item.canonical_name,
            localized_names=item.localized_names or {},
            description=item.description,
            localized_descriptions=item.localized_descriptions or {},
            price=item.price,
            is_veg=item.is_veg,
            ingredients=item.ingredients or [],
            spice_level=item.spice_level,
            available=item.available,
            customizations=item.customizations or [],
            image_url=item.image_url,
            display_name=display_name,
            display_description=display_description,
        )
        response_items.append(item_dto)

    return MenuResponse(
        restaurant_id=restaurant_id,
        language=language,
        categories=categories,
        items=response_items,
    )


@router.get(
    "/{restaurant_id}/menu/{item_id}",
    response_model=MenuItemResponse,
    summary="Get individual menu item",
)
def get_menu_item(
    restaurant_id: str,
    item_id: str,
    db: Session = Depends(get_db),
) -> MenuItemResponse:
    """Retrieve details for a single menu item.

    Args:
        restaurant_id (str): Restaurant ID.
        item_id (str): Menu item ID.
        db (Session): Database session.

    Returns:
        MenuItemResponse: Single item details.

    Raises:
        HTTPException: If item is not found.
    """
    item = (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == restaurant_id, MenuItem.id == item_id)
        .first()
    )
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menu item '{item_id}' not found in restaurant '{restaurant_id}'.",
        )

    return MenuItemResponse(
        id=item.id,
        restaurant_id=item.restaurant_id,
        category=item.category,
        canonical_name=item.canonical_name,
        localized_names=item.localized_names or {},
        description=item.description,
        localized_descriptions=item.localized_descriptions or {},
        price=item.price,
        is_veg=item.is_veg,
        ingredients=item.ingredients or [],
        spice_level=item.spice_level,
        available=item.available,
        customizations=item.customizations or [],
        image_url=item.image_url,
        display_name=item.canonical_name,
        display_description=item.description,
    )
