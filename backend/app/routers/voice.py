"""Voice interaction router for transcription, conversational ordering, and TTS synthesis."""

import logging
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    ConversationRequest,
    ConversationResponse,
    SynthesizeRequest,
    SynthesizeResponse,
    TranscribeResponse,
)
from app.services.conversation import process_message
from app.services.sarvam_stt import transcribe_audio
from app.services.sarvam_tts import synthesize_speech
from app.utils.audio import validate_audio_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["Voice"])


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    summary="Transcribe spoken audio via Sarvam STT",
)
async def transcribe_audio_endpoint(
    file: UploadFile = File(..., description="Spoken voice audio file (webm, wav, mp3, etc.)"),
) -> TranscribeResponse:
    """Accept spoken voice audio recording and return transcription text with detected language.

    Validates audio format and max file size (10MB).

    Args:
        file (UploadFile): Audio recording upload.

    Returns:
        TranscribeResponse: Transcript and detected language code.

    Raises:
        HTTPException: On invalid audio or upstream STT failure.
    """
    audio_bytes = await validate_audio_file(file)
    filename = file.filename or "recording.wav"
    content_type = file.content_type or "audio/wav"

    result = await transcribe_audio(
        audio_bytes=audio_bytes,
        filename=filename,
        content_type=content_type,
    )

    return TranscribeResponse(
        transcript=result.get("transcript", ""),
        language_code=result.get("language_code", "en-IN"),
        request_id=result.get("request_id"),
    )


@router.post(
    "/converse",
    response_model=ConversationResponse,
    summary="Process customer conversational voice/text message",
)
async def converse_endpoint(
    payload: ConversationRequest,
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Core conversational endpoint that processes user messages, updates cart, and formulates response.

    Args:
        payload (ConversationRequest): Customer input text, language, cart state, and dialogue history.
        db (Session): Database session.

    Returns:
        ConversationResponse: Spoken response, cart actions, and current cart state.
    """
    return await process_message(
        text=payload.text,
        language=payload.language,
        restaurant_id=payload.restaurant_id,
        table_id=payload.table_id,
        conversation_history=payload.conversation_history,
        current_cart=payload.current_cart,
        db=db,
    )


@router.post(
    "/synthesize",
    response_model=SynthesizeResponse,
    summary="Synthesize speech audio via Sarvam TTS",
)
async def synthesize_speech_endpoint(
    payload: SynthesizeRequest,
) -> SynthesizeResponse:
    """Synthesize text into natural Indic speech using Sarvam Bulbul TTS.

    Args:
        payload (SynthesizeRequest): Input text and target language code.

    Returns:
        SynthesizeResponse: Base64-encoded audio payload.

    Raises:
        HTTPException: If synthesis fails or service unavailable.
    """
    audio_base64 = await synthesize_speech(
        text=payload.text,
        language_code=payload.language_code,
    )

    return SynthesizeResponse(
        audio_base64=audio_base64,
    )
