from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Any
import os
import shutil
import mimetypes
import tempfile
import io
import time
from pathlib import Path
from datetime import datetime
from PIL import Image, ExifTags
from ..database import database, models
from .. import schemas, crypto_utils
from ..services import scanner, thumbnail
from ..config import settings
from ..runtime import vault_state

router = APIRouter(prefix="/api/media", tags=["media"])

def _convert_to_degrees(value):
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return None

def _get_gps_info(exif):
    if not exif or 'GPSInfo' not in exif:
        return None
    
    gps_tags = exif['GPSInfo']
    lat = gps_tags.get(2)
    lat_ref = gps_tags.get(1)
    lon = gps_tags.get(4)
    lon_ref = gps_tags.get(3)

    if lat and lon and lat_ref and lon_ref:
        lat_dec = _convert_to_degrees(lat)
        lon_dec = _convert_to_degrees(lon)
        
        if lat_dec is not None and lon_dec is not None:
            if lat_ref != 'N': lat_dec = -lat_dec
            if lon_ref != 'E': lon_dec = -lon_dec
            return {"lat": lat_dec, "lng": lon_dec}
    
    return None

def get_media_item(db: Session, media_id: int):
    media = db.query(models.Media).options(joinedload(models.Media.album)).filter(models.Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media

@router.get("/", response_model=List[schemas.Media])
def get_media(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.Media).options(joinedload(models.Media.album))\
             .filter(models.Media.is_encrypted == False)\
             .order_by(models.Media.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/vault", response_model=List[schemas.Media])
def get_vault_media(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    if vault_state.get_key() is None:
        raise HTTPException(status_code=403, detail="Vault is locked")
    return db.query(models.Media).options(joinedload(models.Media.album))\
             .filter(models.Media.is_encrypted == True)\
             .order_by(models.Media.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/upload")
def upload_files(files: List[UploadFile] = File(...), db: Session = Depends(database.get_db)):
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    new_ids = []
    
    for file in files:
        try:
            file_path = settings.UPLOAD_DIR / file.filename
            if file_path.exists():
                name = file_path.stem
                ext = file_path.suffix
                file_path = settings.UPLOAD_DIR / f"{name}_{int(time.time())}{ext}"

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type: mime_type = "application/octet-stream"
            
            ext = file_path.suffix.lower()
            if ext in ['.heic', '.heif']: mime_type = "image/heic"
            if ext in ['.cr2', '.nef', '.dng']: mime_type = f"image/x-{ext.lstrip('.')}"

            stat = os.stat(file_path)
            new_media = models.Media(
                filename=file_path.name,
                original_path=file_path.name,
                media_type=mime_type,
                file_size=stat.st_size,
                is_encrypted=False
            )
            db.add(new_media)
            db.flush()
            new_ids.append(new_media.id)
            count += 1
        except Exception:
            continue
    db.commit()
    return {"status": "success", "count": count, "ids": new_ids}

@router.post("/scan")
def trigger_scan(background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    background_tasks.add_task(scanner.scan_storage, db)
    return {"status": "scanning_started"}

@router.get("/{media_id}/details")
def get_media_details(media_id: int, db: Session = Depends(database.get_db)):
    media = db.query(models.Media).filter(models.Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    key = vault_state.get_key()
    
    if media.is_encrypted:
        if key is None: raise HTTPException(status_code=403, detail="Vault locked")
        file_path = settings.VAULT_DIR / Path(media.original_path).name
    else:
        file_path = settings.UPLOAD_DIR / media.original_path

    if not file_path.exists():
        return {"error": "File not found on disk"}

    stat = file_path.stat()
    real_timestamp = stat.st_mtime

    details = {
        "filename": media.filename,
        "size": stat.st_size,
        "mime": media.media_type,
        "width": 0,
        "height": 0,
        "exif": {}
    }

    temp_path = None
    target_path = file_path

    try:
        if media.is_encrypted:
            fd, temp_name = tempfile.mkstemp()
            os.close(fd)
            temp_path = Path(temp_name)
            crypto_utils.decrypt_file_to_disk(file_path, temp_path, key)
            target_path = temp_path

        if media.media_type.startswith("image/"):
            try:
                with Image.open(target_path) as img:
                    details["width"] = img.width
                    details["height"] = img.height
                    
                    exif_raw = img._getexif()
                    if exif_raw:
                        date_str = exif_raw.get(36867) or exif_raw.get(306)
                        if date_str:
                            try:
                                dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                                real_timestamp = dt.timestamp()
                            except ValueError: pass

                        interesting_tags = {
                            'Make': 'make',
                            'Model': 'model',
                            'ISOSpeedRatings': 'iso',
                            'ExposureTime': 'exposure',
                            'FNumber': 'f_number',
                            'FocalLength': 'focal_length',
                            'LensModel': 'lens',
                            'Software': 'software'
                        }

                        for tag_id, value in exif_raw.items():
                            tag_name = ExifTags.TAGS.get(tag_id)
                            if tag_name in interesting_tags:
                                if isinstance(value, str):
                                    value = value.replace('\x00', '').strip()
                                details["exif"][interesting_tags[tag_name]] = str(value)
                            
                            if tag_name == 'GPSInfo':
                                gps_data = _get_gps_info({ 'GPSInfo': value })
                                if gps_data:
                                    details["exif"]["gps"] = gps_data

            except Exception:
                pass

    finally:
        if temp_path and temp_path.exists():
            os.unlink(temp_path)

    details["created"] = real_timestamp
    return details

@router.get("/{media_id}/content")
def get_media_content(media_id: int, db: Session = Depends(database.get_db)):
    media = get_media_item(db, media_id)
    key = vault_state.get_key()

    if media.is_encrypted:
        if key is None: raise HTTPException(status_code=403, detail="Vault locked")
        filename = Path(media.original_path).name 
        file_path = settings.VAULT_DIR / filename
    else:
        file_path = settings.UPLOAD_DIR / media.original_path

    if not file_path.exists(): raise HTTPException(status_code=404, detail="File not found")

    WEB_NATIVE = {'image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/svg+xml'}
    needs_conversion = media.media_type.startswith('image/') and media.media_type not in WEB_NATIVE
    
    if needs_conversion:
        if media.is_encrypted:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    temp_path = Path(tmp.name)
                crypto_utils.decrypt_file_to_disk(file_path, temp_path, key)
                jpeg_bytes = thumbnail.convert_image_to_jpeg_bytes(temp_path)
                if temp_path.exists(): os.unlink(temp_path)
                if jpeg_bytes: return StreamingResponse(io.BytesIO(jpeg_bytes), media_type="image/jpeg")
            except Exception:
                if 'temp_path' in locals() and temp_path.exists(): os.unlink(temp_path)
        else:
            jpeg_bytes = thumbnail.convert_image_to_jpeg_bytes(file_path)
            if jpeg_bytes: return StreamingResponse(io.BytesIO(jpeg_bytes), media_type="image/jpeg")

    if media.is_encrypted:
        return StreamingResponse(crypto_utils.decrypt_file_generator(file_path, key), media_type=media.media_type)
    else:
        return FileResponse(file_path, media_type=media.media_type)

@router.get("/{media_id}/thumbnail")
def get_media_thumbnail(media_id: int, db: Session = Depends(database.get_db)):
    media = get_media_item(db, media_id)
    
    if media.is_encrypted:
        key = vault_state.get_key()
        if key is None: raise HTTPException(status_code=403, detail="Vault locked")
        vault_filename = Path(media.original_path).name
        vault_path = settings.VAULT_DIR / vault_filename
        if not vault_path.exists(): raise HTTPException(status_code=404)

        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                temp_path = Path(tmp.name)
            crypto_utils.decrypt_file_to_disk(vault_path, temp_path, key)
            thumb_bytes = thumbnail.generate_memory_thumbnail(temp_path, media.media_type)
            if temp_path.exists(): os.unlink(temp_path)
            if thumb_bytes: return StreamingResponse(io.BytesIO(thumb_bytes), media_type="image/jpeg")
            else: raise HTTPException(status_code=404)
        except Exception:
            if 'temp_path' in locals() and temp_path.exists(): os.unlink(temp_path)
            raise HTTPException(status_code=500)

    thumb_path_str = media.thumbnail_path or f"thumb_{media.id}.jpg"
    thumb_path = settings.THUMBNAIL_DIR / thumb_path_str
    
    if not thumb_path.exists():
        new_name = thumbnail.generate_thumbnail(media)
        if new_name: return FileResponse(settings.THUMBNAIL_DIR / new_name, media_type="image/jpeg")
        raise HTTPException(status_code=404)
    return FileResponse(thumb_path, media_type="image/jpeg")

@router.post("/bulk/encrypt")
def bulk_encrypt(ids: List[int], db: Session = Depends(database.get_db)):
    key = vault_state.get_key()
    if key is None: raise HTTPException(status_code=403)
    count = 0
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media and not media.is_encrypted:
            source = settings.UPLOAD_DIR / media.original_path
            dest = settings.VAULT_DIR / source.name
            if source.exists():
                try:
                    crypto_utils.encrypt_file(source, dest, key)
                    if dest.exists() and dest.stat().st_size > 0:
                        os.remove(source)
                        if media.thumbnail_path:
                            thumb = settings.THUMBNAIL_DIR / media.thumbnail_path
                            if thumb.exists(): os.remove(thumb)
                        media.is_encrypted = True
                        media.original_path = source.name
                        count += 1
                    else:
                        if dest.exists(): os.remove(dest)
                except Exception:
                    if dest.exists(): os.remove(dest)
    db.commit()
    return {"status": "encrypted", "count": count}

@router.post("/bulk/decrypt")
def bulk_decrypt(ids: List[int], db: Session = Depends(database.get_db)):
    key = vault_state.get_key()
    if key is None: raise HTTPException(status_code=403)
    count = 0
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media and media.is_encrypted:
            source = settings.VAULT_DIR / Path(media.original_path).name
            dest = settings.UPLOAD_DIR / source.name
            if source.exists():
                try:
                    crypto_utils.decrypt_file_to_disk(source, dest, key)
                    if dest.exists() and dest.stat().st_size > 0:
                        os.remove(source)
                        media.is_encrypted = False
                        media.original_path = source.name
                        count += 1
                    else:
                        if dest.exists(): os.remove(dest)
                except Exception:
                    if dest.exists(): os.remove(dest)
    db.commit()
    return {"status": "decrypted", "count": count}

@router.post("/bulk/delete")
def bulk_delete(ids: List[int], db: Session = Depends(database.get_db)):
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media:
            try:
                path = (settings.VAULT_DIR / Path(media.original_path).name) if media.is_encrypted else (settings.UPLOAD_DIR / media.original_path)
                if path.exists(): os.remove(path)
                if media.thumbnail_path:
                    thumb = settings.THUMBNAIL_DIR / media.thumbnail_path
                    if thumb.exists(): os.remove(thumb)
            except Exception: pass
            db.delete(media)
    db.commit()
    return {"status": "deleted"}

@router.put("/bulk/album/{album_id}")
def set_album_for_media(album_id: int, ids: List[int], db: Session = Depends(database.get_db)):
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media: media.album_id = album_id
    db.commit()
    return {"status": "updated"}