"""Pydantic v2 schemas for request validation and response serialization."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class MenuItemCustomization(BaseModel):
    """Schema representing an available customization for a menu item."""

    name: str
    options: List[str]

    model_config = ConfigDict(from_attributes=True)


class MenuItemResponse(BaseModel):
    """Schema representing a menu item returned to clients."""

    id: str
    restaurant_id: str
    category: str
    canonical_name: str
    localized_names: Dict[str, str] = Field(default_factory=dict)
    description: str
    localized_descriptions: Dict[str, str] = Field(default_factory=dict)
    price: float
    is_veg: bool
    ingredients: List[str] = Field(default_factory=list)
    spice_level: str
    available: bool
    customizations: List[Dict[str, Any]] = Field(default_factory=list)
    image_url: Optional[str] = None
    display_name: Optional[str] = None
    display_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MenuResponse(BaseModel):
    """Schema representing the full menu response for a restaurant."""

    restaurant_id: str
    language: str = "en-IN"
    categories: List[str]
    items: List[MenuItemResponse]


class RestaurantResponse(BaseModel):
    """Schema representing basic restaurant information."""

    id: str
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    is_demo: bool = True

    model_config = ConfigDict(from_attributes=True)


class OrderItemRequest(BaseModel):
    """Schema for requesting an item to be added to an order."""

    menu_item_id: str
    quantity: int = Field(default=1, ge=1)
    customizations: Dict[str, Any] = Field(default_factory=dict)


class OrderCreateRequest(BaseModel):
    """Schema for initiating a new order."""

    restaurant_id: str
    table_id: str
    language: str = "en-IN"
    items: List[OrderItemRequest] = Field(default_factory=list)


class OrderUpdateRequest(BaseModel):
    """Schema for modifying draft order items."""

    items: List[OrderItemRequest] = Field(default_factory=list)


class OrderItemResponse(BaseModel):
    """Schema representing an individual line item in an order response."""

    id: Optional[int] = None
    menu_item_id: str
    item_name: str
    quantity: int
    customizations: Dict[str, Any] = Field(default_factory=dict)
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    """Schema representing an order and its current status."""

    id: str
    restaurant_id: str
    table_id: str
    status: str
    items: List[OrderItemResponse] = Field(default_factory=list)
    total_amount: float
    created_at: datetime
    updated_at: datetime
    language: str

    model_config = ConfigDict(from_attributes=True)


class KitchenOrderResponse(BaseModel):
    """Schema representing order details formatted for the kitchen display."""

    id: str
    restaurant_id: str
    table_id: str
    status: str
    items: List[OrderItemResponse]
    total_amount: float
    created_at: datetime
    updated_at: datetime
    language: str

    model_config = ConfigDict(from_attributes=True)


OrderStatusLiteral = Literal[
    "pending",
    "accepted",
    "preparing",
    "ready",
    "completed",
    "cancelled",
]


class StatusUpdateRequest(BaseModel):
    """Schema for updating an order status from kitchen display."""

    status: OrderStatusLiteral


class CartItem(BaseModel):
    """Schema representing an item in the client conversation cart."""

    item_id: str
    item_name: str
    quantity: int = Field(default=1, ge=1)
    unit_price: float
    customizations: Dict[str, Any] = Field(default_factory=dict)
    subtotal: Optional[float] = None


class CartUpdateAction(BaseModel):
    """Schema representing an action applied to the cart from voice conversation."""

    type: Literal[
        "add_item",
        "remove_item",
        "modify_quantity",
        "clear_cart",
        "confirm_order",
        "ask_question",
        "unavailable_item",
    ]
    item_id: Optional[str] = None
    item_name: Optional[str] = None
    quantity: Optional[int] = None
    customizations: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None


class ConversationHistoryMessage(BaseModel):
    """Schema representing a single message in conversation history."""

    role: Literal["user", "assistant", "system"]
    content: str


class ConversationRequest(BaseModel):
    """Schema for conversational interaction with VoiceMenu AI."""

    text: str
    language: str = "en-IN"
    restaurant_id: str
    table_id: str
    conversation_history: List[ConversationHistoryMessage] = Field(default_factory=list)
    current_cart: List[CartItem] = Field(default_factory=list)


class ConversationResponse(BaseModel):
    """Schema returned after processing customer voice or text query."""

    response_text: str
    cart_updates: List[CartUpdateAction] = Field(default_factory=list)
    current_cart: List[CartItem] = Field(default_factory=list)
    action: str = "none"
    order_id: Optional[str] = None


class TranscribeResponse(BaseModel):
    """Schema returned after transcribing audio via Sarvam STT."""

    transcript: str
    language_code: str
    request_id: Optional[str] = None


class SynthesizeRequest(BaseModel):
    """Schema for requesting speech synthesis via Sarvam TTS."""

    text: str
    language_code: str = "en-IN"


class SynthesizeResponse(BaseModel):
    """Schema returned containing synthesized base64 audio."""

    audio_base64: str
    request_id: Optional[str] = None
