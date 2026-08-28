import requests
from fastapi import HTTPException

from src.config import settings
from src.constants import ImageTypes
from src.features.image_validation import validate_image

worker_url = settings.R2_WORKER_URL
upload_key = settings.R2_UPLOAD_KEY

def _validate_worker_url_and_key():
    if not worker_url:
        raise ValueError("R2_WORKER_URL is not configured")
    if not upload_key:
        raise ValueError("R2_UPLOAD_KEY is not configured")


def build_object_key(folder, image_reference):
    return f"{folder}/{image_reference}"


def get_object_url(key):
    """Generate worker URL using worker base url and key as UUID."""
    if not key or not worker_url:
        return None
    return f"{worker_url.rstrip('/')}/{key}"


def fetch_image(folder: str, image_reference) -> tuple[bytes, str]:
    """Fetch image bytes from worker using upload key."""

    _validate_worker_url_and_key()
    if not image_reference:
        raise ValueError("imageReference is required")

    key = build_object_key(folder, image_reference)
    url = f"{worker_url.rstrip('/')}/{key}"

    response = requests.get(url, headers={"X-Upload-Key": upload_key}, timeout=30)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Image not found")
    if not response.ok:
        raise HTTPException(
            status_code=502,
            detail=f"R2 fetch failed ({response.status_code}): {response.text}",
        )

    content_type = response.headers.get("Content-Type", "application/octet-stream")
    return response.content, content_type


def fetch_profile_image(image_reference) -> tuple[bytes, str]:
    return fetch_image(ImageTypes.PROFILE.value, image_reference)


def upload_image(folder, image_reference, file: bytes, content_type: str | None = None, filename: str | None = None):
    """Upload images, not necessary to async because router already using async function."""

    _validate_worker_url_and_key()
    if not image_reference or not file:
        raise ValueError("Image path and file are required")

    normalized_content_type = validate_image(content_type, file, filename)

    key = build_object_key(folder, image_reference)
    url = f"{worker_url.rstrip('/')}/{key}"

    response = requests.put(url, headers={"Content-Type": normalized_content_type, "X-Upload-Key": upload_key}, data=file, timeout=30)

    if not response.ok:
        raise HTTPException(
            status_code=502,
            detail=f"R2 upload failed ({response.status_code}): {response.text}",
        )

    return image_reference, True


def remove_image(folder: str, image_reference):
    """Remove image using worker."""

    _validate_worker_url_and_key()
    if not image_reference:
        raise ValueError('imageReference is required')
    
    key = build_object_key(folder, image_reference)
    url = f"{worker_url.rstrip('/')}/{key}"
    
    response = requests.delete(url, headers={"X-Upload-Key": upload_key}, timeout=30)

    if not response.ok:
        try:
            detail = response.text
        except Exception:
            detail = ""
        raise HTTPException(
            status_code=502,
            detail=f"R2 delete failed ({response.status_code}): {detail}",
        )


