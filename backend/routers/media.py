from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
import os
import shutil
import mimetypes
import tempfile
import io
from pathlib import Path
from ..database import database, models
from .. import schemas, crypto_utils
from ..services import scanner, thumbnail
from ..config import settings
from ..runtime import vault_state

router = APIRouter(prefix="/api/media", tags=["media"])

WEB_NATIVE_FORMATS = {'image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/svg+xml'}

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

@router.get("/{media_id}/content")
def get_media_content(media_id: int, db: Session = Depends(database.get_db)):
    media = get_media_item(db, media_id)
    key = vault_state.get_key()

    if media.is_encrypted:
        if key is None:
            raise HTTPException(status_code=403, detail="Vault locked")
        filename = Path(media.original_path).name 
        file_path = settings.VAULT_DIR / filename
    else:
        file_path = settings.UPLOAD_DIR / media.original_path

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    # --- ЛОГИКА КОНВЕРТАЦИИ ---
    needs_conversion = media.media_type.startswith('image/') and media.media_type not in WEB_NATIVE_FORMATS
    
    if needs_conversion:
        if media.is_encrypted:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    temp_path = Path(tmp.name)
                
                crypto_utils.decrypt_file_to_disk(file_path, temp_path, key)
                
                jpeg_bytes = thumbnail.convert_image_to_jpeg_bytes(temp_path)
                
                if temp_path.exists(): os.unlink(temp_path)
                
                if jpeg_bytes:
                    return StreamingResponse(io.BytesIO(jpeg_bytes), media_type="image/jpeg")
            except Exception as e:
                if 'temp_path' in locals() and temp_path.exists(): os.unlink(temp_path)
                print(f"Secure convert error: {e}")
                
        else:
            jpeg_bytes = thumbnail.convert_image_to_jpeg_bytes(file_path)
            if jpeg_bytes:
                return StreamingResponse(io.BytesIO(jpeg_bytes), media_type="image/jpeg")

    if media.is_encrypted:
        return StreamingResponse(
            crypto_utils.decrypt_file_generator(file_path, key),
            media_type=media.media_type
        )
    else:
        return FileResponse(file_path, media_type=media.media_type)

@router.get("/{media_id}/thumbnail")
def get_media_thumbnail(media_id: int, db: Session = Depends(database.get_db)):
    media = get_media_item(db, media_id)
    
    if media.is_encrypted:
        key = vault_state.get_key()
        if key is None:
            raise HTTPException(status_code=403, detail="Vault locked")
            
        vault_filename = Path(media.original_path).name
        vault_path = settings.VAULT_DIR / vault_filename
        
        if not vault_path.exists():
            raise HTTPException(status_code=404, detail="Encrypted file missing")

        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                temp_path = Path(tmp.name)
            
            crypto_utils.decrypt_file_to_disk(vault_path, temp_path, key)
            thumb_bytes = thumbnail.generate_memory_thumbnail(temp_path, media.media_type)
            
            if temp_path.exists(): os.unlink(temp_path)

            if thumb_bytes:
                return StreamingResponse(io.BytesIO(thumb_bytes), media_type="image/jpeg")
            else:
                raise HTTPException(status_code=404, detail="Could not generate thumbnail")
                
        except Exception:
            if 'temp_path' in locals() and temp_path.exists(): os.unlink(temp_path)
            raise HTTPException(status_code=500, detail="Thumbnail generation failed")

    thumb_path_str = media.thumbnail_path
    if not thumb_path_str:
         thumb_path_str = f"thumb_{media.id}.jpg"

    thumb_path = settings.THUMBNAIL_DIR / thumb_path_str
    
    if not thumb_path.exists():
        new_name = thumbnail.generate_thumbnail(media)
        if new_name:
            return FileResponse(settings.THUMBNAIL_DIR / new_name, media_type="image/jpeg")
        raise HTTPException(status_code=404, detail="Thumbnail not found")
        
    return FileResponse(thumb_path, media_type="image/jpeg")

@router.post("/bulk/encrypt")
def bulk_encrypt(ids: List[int], db: Session = Depends(database.get_db)):
    key = vault_state.get_key()
    if key is None:
        raise HTTPException(status_code=403, detail="Vault locked")
        
    encrypted_count = 0
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media and not media.is_encrypted:
            source_path = settings.UPLOAD_DIR / media.original_path
            
            filename = source_path.name
            dest_path = settings.VAULT_DIR / filename
            
            if source_path.exists():
                try:
                    crypto_utils.encrypt_file(source_path, dest_path, key)
                    
                    if dest_path.exists() and dest_path.stat().st_size > 0:
                        os.remove(source_path)
                        
                        if media.thumbnail_path:
                            thumb_path = settings.THUMBNAIL_DIR / media.thumbnail_path
                            if thumb_path.exists():
                                try: os.remove(thumb_path)
                                except: pass
                            
                        media.is_encrypted = True
                        media.original_path = filename 
                        encrypted_count += 1
                    else:
                        if dest_path.exists(): os.remove(dest_path)
                except Exception as e:
                    print(f"Encryption error: {e}")
                    if dest_path.exists(): os.remove(dest_path)

    db.commit()
    return {"status": "encrypted", "count": encrypted_count}

@router.post("/bulk/decrypt")
def bulk_decrypt(ids: List[int], db: Session = Depends(database.get_db)):
    key = vault_state.get_key()
    if key is None:
        raise HTTPException(status_code=403, detail="Vault locked")

    decrypted_count = 0
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media and media.is_encrypted:
            filename = Path(media.original_path).name
            source_path = settings.VAULT_DIR / filename
            
            dest_path = settings.UPLOAD_DIR / filename
            
            if source_path.exists():
                try:
                    crypto_utils.decrypt_file_to_disk(source_path, dest_path, key)
                    
                    if dest_path.exists() and dest_path.stat().st_size > 0:
                        os.remove(source_path)
                        media.is_encrypted = False
                        media.original_path = filename
                        decrypted_count += 1
                    else:
                         if dest_path.exists(): os.remove(dest_path)

                except Exception:
                    if dest_path.exists(): os.remove(dest_path)

    db.commit()
    return {"status": "decrypted", "count": decrypted_count}

@router.post("/bulk/delete")
def bulk_delete(ids: List[int], db: Session = Depends(database.get_db)):
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media:
            try:
                if media.is_encrypted:
                    filename = Path(media.original_path).name
                    file_path = settings.VAULT_DIR / filename
                else:
                    file_path = settings.UPLOAD_DIR / media.original_path
                
                if file_path.exists(): os.remove(file_path)
                
                if media.thumbnail_path:
                    thumb_path = settings.THUMBNAIL_DIR / media.thumbnail_path
                    if thumb_path.exists(): os.remove(thumb_path)
            except Exception:
                pass
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