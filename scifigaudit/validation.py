MAX_BYTES = 10 * 1024 * 1024
ALLOWED_MIME = {"image/png", "image/jpeg", "image/tiff"}


def validate_upload(data: bytes, mime_type: str | None) -> str | None:
    if not data:
        return "The uploaded file is empty."
    if len(data) > MAX_BYTES:
        return "The image exceeds the 10 MB application limit."
    if mime_type and mime_type not in ALLOWED_MIME:
        return "Only PNG, JPEG, and TIFF images are supported."
    signatures = (b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"II*\x00", b"MM\x00*")
    if not any(data.startswith(signature) for signature in signatures):
        return "The file signature does not match a supported image format."
    return None

