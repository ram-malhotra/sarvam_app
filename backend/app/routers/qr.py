"""Table QR code generation router for seamless customer table onboarding."""

import io
import logging
from fastapi import APIRouter, Query, Response, status
import qrcode

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/qr", tags=["Table QR Codes"])


@router.get(
    "/{restaurant_id}/{table_id}",
    summary="Generate table onboarding QR code PNG",
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Returns raw PNG image bytes for the table QR code.",
        }
    },
)
def generate_table_qr_code(
    restaurant_id: str,
    table_id: str,
    base_url: str = Query(
        default="http://localhost:5173",
        description="Frontend base URL for table routing",
    ),
) -> Response:
    """Generate a high-contrast PNG QR code directing diners to their digital voice table.

    The QR code encodes URL format: {base_url}/r/{restaurant_id}/{table_id}

    Args:
        restaurant_id (str): Restaurant ID.
        table_id (str): Table identifier (e.g. 'table-4', 'T12').
        base_url (str): Web client host address.

    Returns:
        Response: PNG image stream.
    """
    clean_base = base_url.rstrip("/")
    target_url = f"{clean_base}/r/{restaurant_id}/{table_id}"

    logger.info("Generating QR code for destination: %s", target_url)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    png_bytes = buffer.getvalue()

    return Response(
        content=png_bytes,
        media_type="image/png",
        status_code=status.HTTP_200_OK,
        headers={
            "Content-Disposition": f'inline; filename="qr-{restaurant_id}-{table_id}.png"',
            "Cache-Control": "public, max-age=86400",
        },
    )
