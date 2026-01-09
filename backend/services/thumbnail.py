import os
import io
from PIL import Image, ImageOps
import cv2
from pathlib import Path
from ..config import settings

# --- Подключаем поддержку HEIC ---
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
    HAS_HEIF = True
except ImportError:
    HAS_HEIF = False
    print("Warning: pillow-heif not installed. HEIC support disabled.")

# --- Подключаем поддержку RAW ---
try:
    import rawpy
    HAS_RAW = True
except ImportError:
    HAS_RAW = False
    print("Warning: rawpy not installed. Advanced RAW support disabled.")

def generate_thumbnail(media_item, _unused=None) -> str:
    if not media_item.original_path:
        return None
        
    thumb_filename = f"thumb_{media_item.id}.jpg"
    thumb_path = settings.THUMBNAIL_DIR / thumb_filename
    
    if thumb_path.exists():
        return thumb_filename
        
    filename = Path(media_item.original_path).name
    if media_item.is_encrypted:
        source_path = settings.VAULT_DIR / filename
    else:
        source_path = settings.UPLOAD_DIR / media_item.original_path
    
    if not source_path.exists():
        return None
    
    try:
        img = None
        
        if media_item.media_type and media_item.media_type.startswith('video/'):
            img = _extract_video_frame(source_path)

        if img is None:
            img = _load_image_robust(source_path)

        if img is None:
            return None

        try: img = ImageOps.exif_transpose(img)
        except Exception: pass

        if img.mode in ("RGBA", "P", "CMYK"): 
            img = img.convert("RGB")
            
        img.thumbnail((400, 400), Image.Resampling.LANCZOS)
        img.save(thumb_path, "JPEG", quality=85)
        
        return thumb_filename

    except Exception as e:
        print(f"Thumb error for {media_item.id}: {e}")
        return None

def generate_memory_thumbnail(file_path: Path, media_type: str) -> bytes:
    try:
        img = None
        if media_type and media_type.startswith('video/'):
            img = _extract_video_frame(file_path)
        else:
            img = _load_image_robust(file_path)
            
        if img:
            try: img = ImageOps.exif_transpose(img)
            except: pass
            if img.mode != "RGB": img = img.convert("RGB")
            
            img.thumbnail((400, 400), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=80)
            return output.getvalue()
    except Exception as e:
        print(f"Memory thumb error: {e}")
    return None

def convert_image_to_jpeg_bytes(file_path: Path) -> bytes:
    try:
        img = _load_image_robust(file_path)
        if img:
            try: img = ImageOps.exif_transpose(img)
            except: pass
            if img.mode != "RGB": img = img.convert("RGB")
            
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=90) 
            return output.getvalue()
    except Exception as e:
        print(f"Conversion error: {e}")
    return None

# --- Helpers ---

def _extract_video_frame(path: Path):
    try:
        cap = cv2.VideoCapture(str(path))
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_POS_MSEC, 1000)
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = cap.read()
            cap.release()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return Image.fromarray(frame_rgb)
    except Exception:
        pass
    return None

def _load_image_robust(path: Path):
    str_path = str(path)
    ext = path.suffix.lower()

    if HAS_RAW and ext in ['.cr2', '.nef', '.dng', '.arw', '.orf', '.rw2']:
        try:
            with rawpy.imread(str_path) as raw:
                rgb = raw.postprocess(use_camera_wb=True)
                return Image.fromarray(rgb)
        except Exception as e:
            print(f"Rawpy failed for {path}: {e}, trying Pillow")

    try:
        img = Image.open(path)
        img.load() # Force load
        return img
    except Exception as e:
        print(f"Pillow load failed for {path}: {e}")
    
    return None