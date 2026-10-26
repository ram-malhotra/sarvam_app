"""Sarvam Translation service with database caching and fallback mechanisms."""

import logging
from typing import Optional
from sqlalchemy.orm import Session
import httpx
from app.config import get_settings
from app.models import TranslationCache

logger = logging.getLogger(__name__)

SARVAM_TRANSLATE_URL = "https://api.sarvam.ai/translate"
DEFAULT_TRANSLATE_MODEL = "sarvam-translate:v1"


async def translate_text(
    text: str,
    source_lang: str,
    target_lang: str,
    db: Session,
) -> str:
    """Translate text between Indic and English languages with caching.

    Checks the local database cache first. On miss, queries Sarvam's translate API
    and persists the result in TranslationCache.

    Args:
        text (str): Source text string.
        source_lang (str): Source language code (e.g., 'en-IN', 'hi-IN').
        target_lang (str): Target language code (e.g., 'hi-IN', 'ta-IN').
        db (Session): SQLAlchemy database session.

    Returns:
        str: Translated text or original text if unchanged/error occurs.
    """
    clean_text = text.strip()
    if not clean_text or source_lang == target_lang:
        return text

    # 1. Query TranslationCache
    try:
        cached_entry = (
            db.query(TranslationCache)
            .filter(
                TranslationCache.source_text == clean_text,
                TranslationCache.source_lang == source_lang,
                TranslationCache.target_lang == target_lang,
            )
            .first()
        )
        if cached_entry:
            logger.debug("Translation cache hit for text length %d.", len(clean_text))
            return cached_entry.translated_text
    except Exception as exc:
        logger.warning("Error checking translation cache: %s", exc)

    # 2. Check API key configuration
    settings = get_settings()
    api_key = settings.SARVAM_API_KEY.strip() if settings.SARVAM_API_KEY else ""

    if not api_key:
        logger.warning("Sarvam API key not configured; returning original text without translation.")
        return text

    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "input": clean_text,
        "source_language_code": source_lang,
        "target_language_code": target_lang,
        "model": DEFAULT_TRANSLATE_MODEL,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                SARVAM_TRANSLATE_URL,
                headers=headers,
                json=payload,
            )

        if response.status_code != 200:
            logger.error("Sarvam translate API returned status %d: %s", response.status_code, response.text)
            return text

        result = response.json()
        translated_text = result.get("translated_text", clean_text)

        # 3. Cache the translation
        try:
            cache_entry = TranslationCache(
                source_text=clean_text,
                source_lang=source_lang,
                target_lang=target_lang,
                translated_text=translated_text,
            )
            db.add(cache_entry)
            db.commit()
            logger.info("Cached new translation from %s to %s.", source_lang, target_lang)
        except Exception as cache_exc:
            db.rollback()
            logger.warning("Failed to commit translation cache entry: %s", cache_exc)

        return translated_text

    except (httpx.RequestError, httpx.TimeoutException) as net_exc:
        logger.error("Network error during translation request: %s", net_exc)
        return text
