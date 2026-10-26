"""SQLAlchemy ORM models and database entities for VoiceMenu AI."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.database import Base


class Restaurant(Base):
    """Restaurant entity representing a dining venue."""

    __tablename__ = "restaurants"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=True)
    is_demo = Column(Boolean, default=True, nullable=False)

    menu_items = relationship(
        "MenuItem",
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )
    orders = relationship(
        "Order",
        back_populates="restaurant",
        cascade="all, delete-orphan",
    )


class MenuItem(Base):
    """Menu item offered by a restaurant."""

    __tablename__ = "menu_items"

    id = Column(String, primary_key=True, index=True)
    restaurant_id = Column(
        String,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True,
    )
    category = Column(String, nullable=False, index=True)
    canonical_name = Column(String, nullable=False)
    localized_names = Column(JSON, default=dict, nullable=False)
    description = Column(Text, nullable=False)
    localized_descriptions = Column(JSON, default=dict, nullable=False)
    price = Column(Float, nullable=False)
    is_veg = Column(Boolean, default=True, nullable=False)
    ingredients = Column(JSON, default=list, nullable=False)
    spice_level = Column(String, default="mild", nullable=False)
    available = Column(Boolean, default=True, nullable=False)
    customizations = Column(JSON, default=list, nullable=False)
    image_url = Column(String, nullable=True)

    restaurant = relationship("Restaurant", back_populates="menu_items")


class Order(Base):
    """Customer food order for a specific table."""

    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    restaurant_id = Column(
        String,
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True,
    )
    table_id = Column(String, nullable=False, index=True)
    status = Column(
        String,
        default="pending",
        nullable=False,
        index=True,
    )  # pending, accepted, preparing, ready, completed, cancelled
    total_amount = Column(Float, default=0.0, nullable=False)
    language = Column(String, default="en-IN", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )
    restaurant = relationship("Restaurant", back_populates="orders")


class OrderItem(Base):
    """Individual line item associated with an order."""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    order_id = Column(
        String,
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )
    menu_item_id = Column(
        String,
        ForeignKey("menu_items.id"),
        nullable=False,
    )
    item_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    customizations = Column(JSON, default=dict, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")


class TranslationCache(Base):
    """Persistent cache for Sarvam translations to reduce external API overhead."""

    __tablename__ = "translation_cache"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    source_text = Column(Text, nullable=False)
    source_lang = Column(String(16), nullable=False)
    target_lang = Column(String(16), nullable=False)
    translated_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "source_text",
            "source_lang",
            "target_lang",
            name="uq_translation_cache",
        ),
    )


# Re-export schemas for backward/alternative import compatibility
from app.schemas import (  # noqa: E402
    MenuItemCustomization,
    MenuItemResponse,
    MenuResponse,
    RestaurantResponse,
    OrderItemRequest,
    OrderCreateRequest,
    OrderUpdateRequest,
    OrderItemResponse,
    OrderResponse,
    KitchenOrderResponse,
    StatusUpdateRequest,
    CartItem,
    CartUpdateAction,
    ConversationHistoryMessage,
    ConversationRequest,
    ConversationResponse,
    TranscribeResponse,
    SynthesizeRequest,
    SynthesizeResponse,
)

