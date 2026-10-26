"""Conversational ordering service combining Sarvam LLM, prompt engineering, and order engine."""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models import MenuItem, Restaurant
from app.schemas import (
    CartItem,
    CartUpdateAction,
    ConversationHistoryMessage,
    ConversationRequest,
    ConversationResponse,
)
from app.services.order_engine import (
    create_draft_order,
    confirm_order,
    match_menu_items,
    validate_order_item,
)
from app.services.sarvam_chat import chat_completion

logger = logging.getLogger(__name__)


def build_system_prompt(
    restaurant: Restaurant,
    menu_items: List[MenuItem],
    current_cart: List[CartItem],
    language: str,
) -> str:
    """Construct structured system prompt with menu data, current cart, and strict ordering rules.

    Args:
        restaurant (Restaurant): Restaurant database entity.
        menu_items (List[MenuItem]): All available menu items.
        current_cart (List[CartItem]): Current customer cart items.
        language (str): Target language code (e.g. en-IN, hi-IN, ta-IN, te-IN).

    Returns:
        str: Detailed system prompt for Sarvam LLM.
    """
    menu_summary = []
    for m in menu_items:
        loc_name = ""
        if isinstance(m.localized_names, dict):
            loc_name = m.localized_names.get(language, "")
        name_str = f"{m.canonical_name}" + (f" ({loc_name})" if loc_name else "")

        menu_summary.append({
            "id": m.id,
            "name": name_str,
            "category": m.category,
            "price": m.price,
            "is_veg": m.is_veg,
            "spice_level": m.spice_level,
            "available": m.available,
            "customizations": m.customizations,
            "description": m.description,
        })

    cart_summary = [
        {
            "item_id": c.item_id,
            "name": c.item_name,
            "quantity": c.quantity,
            "unit_price": c.unit_price,
            "subtotal": c.subtotal or round(c.unit_price * c.quantity, 2),
            "customizations": c.customizations,
        }
        for c in current_cart
    ]

    prompt = f"""You are VoiceMenu AI, the warm, polite, and efficient voice-first food ordering assistant for "{restaurant.name}".
You are assisting a customer seated at their table.

TARGET LANGUAGE: {language}
You MUST answer in {language} (use the native script if Hindi, Tamil, Telugu, or English).

CURRENT MENU CATALOG:
{json.dumps(menu_summary, ensure_ascii=False, indent=2)}

CUSTOMER'S CURRENT CART:
{json.dumps(cart_summary, ensure_ascii=False, indent=2)}

STRICT OPERATIONAL RULES:
1. NEVER invent or hallucinate items, prices, or options not in the menu catalog.
2. NEVER add unavailable items to the cart. If a requested item has "available": false (e.g. Chicken 65), inform the customer warmly that it is currently sold out and suggest an available alternative.
3. NEVER automatically confirm or place an order unless the customer explicitly commands you to confirm/place/finalize the order.
4. Only add or modify items when the customer explicitly asks to order, add, or change items.
5. If the customer asks questions about ingredients, spice level, or veg options, answer concisely based on the menu catalog.
6. If the customer wants to add an item that has customizations (like spice level or portion), ask for their preference if not mentioned.

MANDATORY OUTPUT FORMAT:
You MUST respond with a single valid JSON object strictly adhering to this schema:
{{
  "response_text": "Spoken response to the customer in {language}",
  "actions": [
    {{
      "type": "add_item" | "remove_item" | "modify_quantity" | "clear_cart" | "confirm_order" | "ask_question",
      "item_id": "exact_item_id_from_menu",
      "quantity": 1,
      "customizations": {{}}
    }}
  ]
}}

Do NOT include any markdown code fencing, markdown backticks, or text outside the JSON object.
"""
    return prompt.strip()


def parse_llm_json(raw_text: str) -> Dict[str, Any]:
    """Clean and parse JSON from LLM output, stripping code fences if present.

    Args:
        raw_text (str): Raw output string from LLM.

    Returns:
        Dict[str, Any]: Parsed JSON dictionary.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback to regex extraction of first {...}
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return {
            "response_text": raw_text,
            "actions": [],
        }


def fallback_rule_based_processor(
    text: str,
    language: str,
    restaurant: Restaurant,
    menu_items: List[MenuItem],
    current_cart: List[CartItem],
) -> Tuple[str, List[CartUpdateAction], str]:
    """Deterministic natural language parser fallback when Sarvam LLM is not configured or fails.

    Args:
        text (str): Customer user message.
        language (str): Ordering language code.
        restaurant (Restaurant): Restaurant entity.
        menu_items (List[MenuItem]): Menu catalog.
        current_cart (List[CartItem]): Current cart.

    Returns:
        Tuple[str, List[CartUpdateAction], str]: (response_text, cart_actions, overall_action)
    """
    lower = text.lower().strip()
    actions: List[CartUpdateAction] = []
    overall_action = "none"

    # Confirm order intent
    if any(k in lower for k in ["confirm", "place order", "checkout", "order kar do", "order panni"]):
        if not current_cart:
            resp = "Your cart is currently empty. Please select delicious items from our menu first!"
            return resp, [], "none"
        return "I am confirming your order right now. Thank you!", [CartUpdateAction(type="confirm_order")], "confirm_order"

    # Clear cart intent
    if any(k in lower for k in ["clear cart", "empty cart", "cancel all", "sab hatao"]):
        return "I have cleared all items from your cart.", [CartUpdateAction(type="clear_cart")], "clear_cart"

    # Quantity parsing
    qty = 1
    num_match = re.search(r"\b(\d+)\b", lower)
    if num_match:
        qty = max(1, int(num_match.group(1)))
    elif "two" in lower or "दो" in lower or "இரண்டு" in lower or "రెండు" in lower:
        qty = 2
    elif "three" in lower or "तीन" in lower or "மூன்று" in lower or "మూడు" in lower:
        qty = 3
    elif "four" in lower or "चार" in lower:
        qty = 4

    # Remove item intent
    if any(k in lower for k in ["remove", "delete", "hatao", "nikalo", "edunga"]):
        matched = match_menu_items(lower, menu_items)
        if matched:
            target_item, _ = matched[0]
            action = CartUpdateAction(type="remove_item", item_id=target_item.id, item_name=target_item.canonical_name)
            resp = f"Removed {target_item.canonical_name} from your cart."
            return resp, [action], "update_cart"
        return "Which item would you like me to remove?", [], "ask_question"

    # Add item intent
    matched_candidates = match_menu_items(lower, menu_items)
    if matched_candidates:
        target_item, score = matched_candidates[0]
        if score >= 0.5:
            if not target_item.available:
                resp = f"I am sorry, but {target_item.canonical_name} is currently sold out. May I recommend another dish?"
                return resp, [CartUpdateAction(type="unavailable_item", item_id=target_item.id, item_name=target_item.canonical_name)], "none"

            action = CartUpdateAction(
                type="add_item",
                item_id=target_item.id,
                item_name=target_item.canonical_name,
                quantity=qty,
                customizations={},
            )
            item_display = target_item.canonical_name
            if isinstance(target_item.localized_names, dict) and language in target_item.localized_names:
                item_display = f"{target_item.canonical_name} ({target_item.localized_names[language]})"
            resp = f"Added {qty} portion(s) of {item_display} to your cart. Anything else?"
            return resp, [action], "update_cart"

    # General greeting or question
    if any(k in lower for k in ["hi", "hello", "namaste", "vanakkam", "menu", "kya hai"]):
        veg_count = sum(1 for m in menu_items if m.is_veg and m.available)
        resp = f"Welcome to {restaurant.name}! We have {len(menu_items)} delicious items including {veg_count} vegetarian specialties like Masala Dosa, Filter Coffee, and Idli. What would you like to order?"
        return resp, [], "ask_question"

    resp = f"I heard '{text}'. Could you please repeat or specify which dish you would like to order?"
    return resp, [], "ask_question"


async def process_message(
    text: str,
    language: str,
    restaurant_id: str,
    table_id: str,
    conversation_history: List[ConversationHistoryMessage],
    current_cart: List[CartItem],
    db: Session,
) -> ConversationResponse:
    """Process customer voice or text query, invoking Sarvam Chat or rule-based fallback, and update cart.

    Args:
        text (str): Spoken or typed user input.
        language (str): Conversation language code.
        restaurant_id (str): ID of the restaurant.
        table_id (str): Table code.
        conversation_history (List[ConversationHistoryMessage]): Dialogue history.
        current_cart (List[CartItem]): Current client cart items.
        db (Session): SQLAlchemy database session.

    Returns:
        ConversationResponse: Updated cart, assistant spoken reply, and actions.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        restaurant = db.query(Restaurant).filter(Restaurant.id == "demo-restaurant").first()
        if restaurant:
            restaurant_id = restaurant.id
    if not restaurant:
        return ConversationResponse(
            response_text=f"Restaurant '{restaurant_id}' could not be located.",
            cart_updates=[],
            current_cart=current_cart,
            action="none",
        )

    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == restaurant_id)
        .all()
    )
    menu_map = {m.id: m for m in menu_items}

    settings = get_settings()
    has_api_key = bool(settings.SARVAM_API_KEY and settings.SARVAM_API_KEY.strip())

    parsed_actions: List[Dict[str, Any]] = []
    response_text = ""
    overall_action = "none"

    if has_api_key:
        system_prompt = build_system_prompt(restaurant, menu_items, current_cart, language)
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

        for h in conversation_history[-6:]:  # keep last 6 turns for context
            messages.append({"role": h.role, "content": h.content})

        messages.append({"role": "user", "content": text})

        try:
            llm_output = await chat_completion(messages, temperature=0.2)
            parsed_json = parse_llm_json(llm_output)
            response_text = parsed_json.get("response_text", "")
            parsed_actions = parsed_json.get("actions", [])
        except Exception as exc:
            logger.warning("Sarvam Chat API call failed, falling back to rule processor: %s", exc)
            fallback_resp, fb_actions, fb_action = fallback_rule_based_processor(
                text, language, restaurant, menu_items, current_cart
            )
            response_text = fallback_resp
            parsed_actions = [a.model_dump() for a in fb_actions]
            overall_action = fb_action
    else:
        logger.info("Operating in standalone/demo mode without Sarvam API key.")
        fallback_resp, fb_actions, fb_action = fallback_rule_based_processor(
            text, language, restaurant, menu_items, current_cart
        )
        response_text = fallback_resp
        parsed_actions = [a.model_dump() for a in fb_actions]
        overall_action = fb_action

    # Apply actions to working cart
    updated_cart: List[CartItem] = [c.model_copy() for c in current_cart]
    applied_actions: List[CartUpdateAction] = []
    confirmed_order_id: Optional[str] = None

    for action_dict in parsed_actions:
        action_type = action_dict.get("type", "")
        item_id = action_dict.get("item_id")
        qty = int(action_dict.get("quantity", 1) or 1)
        customizations = action_dict.get("customizations") or {}

        if action_type == "add_item" and item_id:
            menu_item = menu_map.get(item_id)
            if not menu_item:
                logger.warning("Action attempted to add unknown item_id: %s", item_id)
                continue

            if not menu_item.available:
                applied_actions.append(
                    CartUpdateAction(
                        type="unavailable_item",
                        item_id=menu_item.id,
                        item_name=menu_item.canonical_name,
                        reason="Item is sold out",
                    )
                )
                continue

            # Check if item with matching id already in cart
            existing_cart_item = next(
                (c for c in updated_cart if c.item_id == item_id and c.customizations == customizations),
                None,
            )
            if existing_cart_item:
                existing_cart_item.quantity += qty
                existing_cart_item.subtotal = round(
                    existing_cart_item.quantity * existing_cart_item.unit_price, 2
                )
            else:
                unit_price = round(float(menu_item.price), 2)
                updated_cart.append(
                    CartItem(
                        item_id=menu_item.id,
                        item_name=menu_item.canonical_name,
                        quantity=qty,
                        unit_price=unit_price,
                        customizations=customizations,
                        subtotal=round(unit_price * qty, 2),
                    )
                )

            applied_actions.append(
                CartUpdateAction(
                    type="add_item",
                    item_id=menu_item.id,
                    item_name=menu_item.canonical_name,
                    quantity=qty,
                    customizations=customizations,
                )
            )
            overall_action = "update_cart"

        elif action_type == "remove_item" and item_id:
            updated_cart = [c for c in updated_cart if c.item_id != item_id]
            applied_actions.append(
                CartUpdateAction(
                    type="remove_item",
                    item_id=item_id,
                )
            )
            overall_action = "update_cart"

        elif action_type == "modify_quantity" and item_id:
            target_cart_item = next((c for c in updated_cart if c.item_id == item_id), None)
            if target_cart_item:
                if qty <= 0:
                    updated_cart = [c for c in updated_cart if c.item_id != item_id]
                else:
                    target_cart_item.quantity = qty
                    target_cart_item.subtotal = round(qty * target_cart_item.unit_price, 2)
            applied_actions.append(
                CartUpdateAction(
                    type="modify_quantity",
                    item_id=item_id,
                    quantity=qty,
                )
            )
            overall_action = "update_cart"

        elif action_type == "clear_cart":
            updated_cart.clear()
            applied_actions.append(CartUpdateAction(type="clear_cart"))
            overall_action = "clear_cart"

        elif action_type == "confirm_order":
            if updated_cart:
                order_items_payload = [
                    {
                        "menu_item_id": c.item_id,
                        "quantity": c.quantity,
                        "customizations": c.customizations,
                    }
                    for c in updated_cart
                ]
                try:
                    draft = create_draft_order(
                        restaurant_id=restaurant_id,
                        table_id=table_id,
                        items=order_items_payload,
                        language=language,
                        db=db,
                    )
                    confirmed = confirm_order(draft.id, db)
                    confirmed_order_id = confirmed.id
                    overall_action = "confirm_order"
                    applied_actions.append(CartUpdateAction(type="confirm_order"))
                    # Clear cart after confirmed order
                    updated_cart.clear()
                except Exception as order_exc:
                    logger.error("Failed to confirm order from voice flow: %s", order_exc)
                    response_text += f" (Could not place order: {str(order_exc)})"

    return ConversationResponse(
        response_text=response_text,
        cart_updates=applied_actions,
        current_cart=updated_cart,
        action=overall_action,
        order_id=confirmed_order_id,
    )
