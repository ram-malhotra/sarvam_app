"""Audio file validation utilities for VoiceMenu AI."""

import logging
from typing import List
from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_TYPES: List[str] = [
    "audio/webm",
    "audio/wav",
    "audio/wave",
    "audio/x-wav",
    "audio/mpeg",
    "audio/mp3",
    "audio/ogg",
    "audio/flac",
    "audio/aac",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
]

MAX_AUDIO_SIZE: int = 10 * 1024 * 1024  # 10MB limit


async def validate_audio_file(file: UploadFile) -> bytes:
    """Validate uploaded audio file MIME type and size, returning raw bytes.

    Args:
        file (UploadFile): FastAPI uploaded file object.

    Returns:
        bytes: Read audio file bytes.

    Raises:
        HTTPException: If file type is unsupported, empty, or exceeds 10MB.
    """
    content_type = (file.content_type or "").lower().split(";")[0].strip()

    if content_type not in ALLOWED_AUDIO_TYPES and not content_type.startswith("audio/"):
        logger.warning("Rejected audio upload with unsupported content-type: %s", content_type)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported audio type '{file.content_type}'. "
                f"Allowed formats: webm, wav, mp3, ogg, flac, aac, mp4."
            ),
        )

    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty (0 bytes).",
        )

    if len(content) > MAX_AUDIO_SIZE:
        logger.warning("Rejected audio file exceeding 10MB limit (%d bytes).", len(content))
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Audio file size ({len(content)} bytes) exceeds the 10MB limit.",
        )

    return content
