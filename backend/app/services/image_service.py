from pathlib import Path
from uuid import uuid4

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def save_uploaded_image(file):
    extension = Path(file.filename).suffix.lower()

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise ValueError("Image file is too large. Maximum size is 10 MB.")

    image_id = uuid4().hex
    filename = f"{image_id}{extension}"
    file_path = UPLOAD_DIR / filename

    file_path.write_bytes(contents)

    return {
        "image_id": image_id,
        "filename": filename,
        "path": str(file_path),
    }