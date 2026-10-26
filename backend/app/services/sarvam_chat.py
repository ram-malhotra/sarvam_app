"""Sarvam Chat Completion service using httpx."""

import logging
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)

SARVAM_CHAT_URL = "https://api.sarvam.ai/v1/chat/completions"
DEFAULT_CHAT_MODEL = "sarvam-105b"


async def chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    """Send conversation messages to Sarvam LLM chat completion API.

    Args:
        messages (List[Dict[str, str]]): List of message dictionaries with role and content.
        temperature (float): Sampling temperature (default: 0.3 for consistency).
        max_tokens (int): Maximum tokens to generate in response.

    Returns:
        str: Assistant response content string.

    Raises:
        HTTPException: If API key is missing or upstream service call fails.
    """
    settings = get_settings()
    api_key = settings.SARVAM_API_KEY.strip() if settings.SARVAM_API_KEY else ""

    if not api_key:
        logger.error("Sarvam API key is not configured for Chat Completion.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sarvam API key is not configured. Please set SARVAM_API_KEY in environment variables.",
        )

    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json",
    }

    # reasoning_effort set to None to disable thinking mode for low latency voice responses
    payload: Dict[str, Any] = {
        "model": DEFAULT_CHAT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "reasoning_effort": None,
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                SARVAM_CHAT_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            logger.error("Sarvam chat completion failed (HTTP %d): %s", response.status_code, response.text)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Sarvam Chat service returned error (HTTP {response.status_code}).",
            )

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            logger.error("Sarvam chat returned no choices: %s", data)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Empty response choices returned by Sarvam Chat API.",
            )

        first_choice = choices[0]
        content = first_choice.get("message", {}).get("content", "")
        return content

    except httpx.TimeoutException as exc:
        logger.error("Timeout connecting to Sarvam Chat API: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout waiting for Sarvam Chat response.",
        ) from exc
    except httpx.RequestError as exc:
        logger.error("Network error communicating with Sarvam Chat API: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Network error communicating with Sarvam Chat service.",
        ) from exc
