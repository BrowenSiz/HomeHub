from PIL import Image
import os
import io
from pathlib import Path
from ..config import settings
from ..database import models

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

def generate_thumbnail(media: models.Media) -> Path:
    source_path = settings.UPLOAD_DIR / Path(media.original_path).name
    if not source_path.exists():
        return None

    target_name = f"thumb_{media.id}.jpg"
    target_path = settings.THUMBNAIL_DIR / target_name
    
    settings.THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)

    try:
        if "video" in media.media_type:
            return _generate_video_thumbnail_file(source_path, target_path)
        else:
            return _generate_image_thumbnail_file(source_path, target_path)
    except Exception as e:
        print(f"Thumbnail generation error for {media.id}: {e}")
        return None

def generate_memory_thumbnail(file_path: Path, media_type: str) -> bytes:
    try:
        if "video" in media_type:
            return _generate_video_thumbnail_bytes(file_path)
        else:
            return _generate_image_thumbnail_bytes(file_path)
    except Exception as e:
        print(f"Memory thumbnail error: {e}")
        return None

def _generate_image_thumbnail_file(source: Path, target: Path) -> Path:
    with Image.open(source) as img:
        img.thumbnail((300, 300))
        if img.mode in ("RGBA", "P"): 
            img = img.convert("RGB")
        img.save(target, "JPEG", quality=80)
    return target

def _generate_video_thumbnail_file(source: Path, target: Path) -> Path:
    if not HAS_CV2: return None
    
    cap = cv2.VideoCapture(str(source))
    success, frame = cap.read()
    cap.release()
    
    if success:
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img.thumbnail((300, 300))
        img.save(target, "JPEG", quality=80)
        return target
    return None

def _generate_image_thumbnail_bytes(source: Path) -> bytes:
    with Image.open(source) as img:
        img.thumbnail((300, 300))
        if img.mode in ("RGBA", "P"): 
            img = img.convert("RGB")
        
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=80)
        return output.getvalue()

def _generate_video_thumbnail_bytes(source: Path) -> bytes:
    if not HAS_CV2: return None

    cap = cv2.VideoCapture(str(source))
    success, frame = cap.read()
    cap.release()

    if success:
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img.thumbnail((300, 300))
        
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=80)
        return output.getvalue()
    return None