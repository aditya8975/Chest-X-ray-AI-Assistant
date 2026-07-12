import uuid
from pathlib import Path
from PIL import Image
from app.config import settings


def unique_stem(original_name: str) -> str:
    return uuid.uuid4().hex


def save_raw_upload(raw_bytes: bytes, filename: str, stem: str) -> str:
    ext = Path(filename).suffix.lower() or ".bin"
    path = settings.upload_dir / f"{stem}{ext}"
    path.write_bytes(raw_bytes)
    return str(path)


def save_display_image(image: Image.Image, stem: str) -> str:
    path = settings.upload_dir / f"{stem}_display.png"
    image.save(path)
    return str(path)


def save_heatmap(image: Image.Image, stem: str, pathology: str) -> str:
    safe_name = pathology.replace(" ", "_")
    path = settings.heatmap_dir / f"{stem}_{safe_name}.png"
    image.save(path)
    return str(path)
