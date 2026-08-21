from fastapi import HTTPException


IMAGE_JPEG = "image/jpeg"

ALLOWED_IMAGE_TYPES = {IMAGE_JPEG, "image/png", "image/webp", "image/gif"}
CONTENT_TYPE_ALIASES = {"image/jpg": IMAGE_JPEG}
HEIC_TYPES = {"image/heic", "image/heif"}
HEIC_EXTENSIONS = (".heic", ".heif")
HEIC_BRANDS = {
    "heic",
    "heix",
    "hevc",
    "hevx",
    "heim",
    "heis",
    "hevm",
    "hevs",
    "mif1",
    "msf1",
}
MAX_SIZE = 5 * 1024 * 1024
HEIC_ERROR = "HEIC/HEIF images are not supported. Please use JPEG, PNG, WebP, or GIF"


def _normalize_content_type(content_type: str | None) -> str:
    mime_type = (content_type or "").split(";")[0].strip().lower()
    return CONTENT_TYPE_ALIASES.get(mime_type, mime_type)


def _bytes_to_ascii(data: bytes, start: int, length: int) -> str:
    return data[start : start + length].decode("ascii", errors="ignore")


def looks_like_heic(data: bytes) -> bool:
    if len(data) < 12:
        return False
    if _bytes_to_ascii(data, 4, 4) != "ftyp":
        return False
    brand = _bytes_to_ascii(data, 8, 4).lower()
    return brand in HEIC_BRANDS


def matches_declared_type(data: bytes, mime_type: str) -> bool:
    if mime_type == IMAGE_JPEG:
        return len(data) >= 3 and data[0] == 0xFF and data[1] == 0xD8 and data[2] == 0xFF
    if mime_type == "image/png":
        return data.startswith(b"\x89PNG")
    if mime_type == "image/gif":
        return _bytes_to_ascii(data, 0, 4) == "GIF8"
    if mime_type == "image/webp":
        return (
            len(data) >= 12
            and _bytes_to_ascii(data, 0, 4) == "RIFF"
            and _bytes_to_ascii(data, 8, 4) == "WEBP"
        )
    return False


def is_heic_by_name_or_type(content_type: str, filename: str | None = None) -> bool:
    if content_type in HEIC_TYPES:
        return True
    name = (filename or "").lower()
    return name.endswith(HEIC_EXTENSIONS)


def validate_image(content_type: str | None, data: bytes, filename: str | None = None) -> str:
    """Validate a browser-displayable image. Rejects HEIC even if renamed to .jpg.

    Returns the normalized MIME type for downstream storage (e.g. R2 Content-Type).
    """
    if not data:
        raise HTTPException(status_code=400, detail="No image selected")

    if not (content_type or "").strip():
        raise HTTPException(status_code=400, detail="Content-Type header is required")

    mime_type = _normalize_content_type(content_type)

    if is_heic_by_name_or_type(mime_type, filename):
        raise HTTPException(status_code=400, detail=HEIC_ERROR)

    if mime_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="File type must be JPEG, PNG, WebP, or GIF")

    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Image must be less than 5MB")

    header = data[:16]

    if looks_like_heic(header):
        raise HTTPException(status_code=400, detail=HEIC_ERROR)

    if not matches_declared_type(header, mime_type):
        raise HTTPException(status_code=400, detail="File content does not match a supported image type (JPEG, PNG, WebP, or GIF)")

    return mime_type
