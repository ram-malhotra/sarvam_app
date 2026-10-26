"""Sarvam Speech-to-Text (STT) service using httpx."""

import logging
from typing import Any, Dict
from fastapi import HTTPException, status
import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)

SARVAM_STT_URL = "https://api.sarvam.ai/speech-to-text"
DEFAULT_STT_MODEL = "saaras:v4"
DEFAULT_STT_MODE = "transcribe"


async def transcribe_audio(
    audio_bytes: bytes,
    filename: str = "audio.wav",
    content_type: str = "audio/wav",
) -> Dict[str, Any]:
    """Transcribe spoken audio bytes to text using Sarvam's Saaras speech-to-text model.

    Args:
        audio_bytes (bytes): Raw audio file bytes.
        filename (str): Name of the uploaded audio file.
        content_type (str): MIME type of the audio.

    Returns:
        Dict[str, Any]: Dictionary containing transcript, language_code, and request_id.

    Raises:
        HTTPException: If API key is missing or upstream Sarvam request fails.
    """
    settings = get_settings()
    api_key = settings.SARVAM_API_KEY.strip() if settings.SARVAM_API_KEY else ""

    if not api_key:
        logger.error("Sarvam API key is not configured. Transcription cannot proceed.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sarvam API key is not configured. Please set SARVAM_API_KEY in environment variables.",
        )

    headers = {
        "api-subscription-key": api_key,
    }

    files = {
        "file": (filename, audio_bytes, content_type),
    }

    data = {
        "model": DEFAULT_STT_MODEL,
        "mode": DEFAULT_STT_MODE,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                SARVAM_STT_URL,
                headers=headers,
                files=files,
                data=data,
            )

        if response.status_code != 200:
            logger.error("Sarvam STT failed with status %d: %s", response.status_code, response.text)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Sarvam Speech-to-Text service returned error (HTTP {response.status_code}).",
            )

        result = response.json()
        transcript = result.get("transcript", "")
        language_code = result.get("language_code", "en-IN")
        request_id = result.get("request_id")

        logger.info(
            "Transcription completed successfully. Detected language: %s, Length: %d chars.",
            language_code,
            len(transcript),
        )

        return {
            "transcript": transcript,
            "language_code": language_code,
            "request_id": request_id,
        }

    except httpx.TimeoutException as exc:
        logger.error("Timeout connecting to Sarvam STT service: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Timeout waiting for Sarvam Speech-to-Text response.",
        ) from exc
    except httpx.RequestError as exc:
        logger.error("Network error communicating with Sarvam STT service: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Network error communicating with Sarvam Speech-to-Text service.",
        ) from exc
