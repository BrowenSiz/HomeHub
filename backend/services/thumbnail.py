import os
from PIL import Image, ImageOps
import cv2
from ..config import settings
from pathlib import Path

def generate_thumbnail(media_item):
    if not media_item.original_path:
        return None
        
    thumb_filename = f"thumb_{media_item.id}.jpg"
    thumb_path = settings.THUMBNAIL_DIR / thumb_filename
    
    if thumb_path.exists():
        return str(thumb_path)
        
    filename = Path(media_item.original_path).name
    if media_item.is_encrypted:
        source_path = settings.VAULT_DIR / filename
    else:
        source_path = settings.UPLOAD_DIR / filename
    
    if not source_path.exists():
        return None
    
    try:
        img = None
        if media_item.media_type and media_item.media_type.startswith('video/'):
            try:
                cap = cv2.VideoCapture(str(source_path))
                if cap.isOpened():
                    cap.set(cv2.CAP_PROP_POS_MSEC, 1000)
                    ret, frame = cap.read()
                    if not ret:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()
                    if ret:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame_rgb)
                    cap.release()
            except Exception: pass

        if img is None:
            try:
                img = Image.open(source_path)
            except IOError: return None

        try: img = ImageOps.exif_transpose(img)
        except Exception: pass

        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            
        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        img.save(thumb_path, "JPEG", quality=85)
        
        return str(thumb_path)

    except Exception as e:
        print(f"Thumb error: {e}")
        return None