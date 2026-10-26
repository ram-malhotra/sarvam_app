"""Sarvam Text-to-Speech (TTS) service using httpx."""

import logging
from typing import Dict
from fastapi import HTTPException, status
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"
DEFAULT_TTS_MODEL = "bulbul:v4-flash"
MAX_TTS_TEXT_LENGTH = 2500

SPEAKER_MAP: Dict[str, str] = {
    "hi-IN": "shubh_hi_customer",
    "en-IN": "simran_en_customer",
    "ta-IN": "gokul_ta_narration",
    "te-IN": "kavitha_te_conversation",
}
DEFAULT_SPEAKER = "simran_en_customer"


async def synthesize_speech(text: str, language_code: str = "en-IN") -> str:
    """Synthesize text into speech audio encoded as a base64 string using Sarvam Bulbul TTS.

    Args:
        text (str): Input text to synthesize.
        language_code (str): Target spoken language code (e.g. 'en-IN', 'hi-IN').

    Returns:
        str: Base64-encoded audio string (WAV/MP3).

    Raises:
        HTTPException: If API key is missing or synthesis fails.
    """
    settings = get_settings()
    api_key = settings.SARVAM_API_KEY.strip() if settings.SARVAM_API_KEY else ""

    if not api_key:
        logger.error("Sarvam API key is not configured. Speech synthesis cannot proceed.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sarvam API key is not configured. Please set SARVAM_API_KEY in environment variables.",
        )

    # Truncate text to 2500 chars limit as per Sarvam API guidelines
    truncated_text = text.strip()[:MAX_TTS_TEXT_LENGTH]
    if not truncated_text:
        return ""

    speaker = SPEAKER_MAP.get(language_code, DEFAULT_SPEAKER)

    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "text": truncated_text,
        "language_code": language_code,
        "model": DEFAULT_TTS_MODEL,
        "speaker": speaker,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                SARVAM_TTS_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            logger.error("Sarvam TTS failed with status %d: %s", response.status_code, response.text)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Sarvam Text-to-Speech service returned error (HTTP {response.status_code}).",
            )

        result = response.json()
        audios = result.get("audios", [])
        if not audios:
            logger.warning("Sarvam TTS returned empty audios array.")
            return ""

        # Join audio base64 fragments if multiple returned
        joined_audio = "".join(audios)
        logger.info(
            "Speech synthesis successful for language %s (%d chars).",
            language_code,
            len(truncated_text),
        )
        return joined_audio

    except httpx.TimeoutException as exc:
        logger.error("Timeout connecting to Sarvam TTS service: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout waiting for Sarvam Text-to-Speech response.",
        ) from exc
    except httpx.RequestError as exc:
        logger.error("Network error communicating with Sarvam TTS service: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Network error communicating with Sarvam Text-to-Speech service.",
        ) from exc
