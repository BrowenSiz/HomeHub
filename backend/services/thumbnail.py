import os
from PIL import Image, ImageOps
import cv2
from ..config import settings

def generate_thumbnail(media_item):
    if not media_item.original_path:
        return None
        
    thumb_filename = f"thumb_{media_item.id}.jpg"
    thumb_path = settings.THUMBNAIL_DIR / thumb_filename
    
    if thumb_path.exists():
        return str(thumb_path)
        
    source_path = media_item.original_path
    
    try:
        img = None
        
        if media_item.media_type.startswith('video/'):
            try:
                cap = cv2.VideoCapture(source_path)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame_rgb)
                    cap.release()
            except Exception as e:
                print(f"Error extracting video frame: {e}")

        # 2. Обработка Фото
        if img is None:
            try:
                img = Image.open(source_path)
            except IOError:
                return None

        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        img.save(thumb_path, "JPEG", quality=80)
        return str(thumb_path)

    except Exception as e:
        print(f"Thumbnail generation failed for {source_path}: {e}")
        return None