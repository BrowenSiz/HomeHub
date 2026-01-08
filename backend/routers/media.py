from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
import os
import shutil
import mimetypes
from pathlib import Path
from ..database import database, models
from .. import schemas
from ..services import scanner, thumbnail
from ..config import settings
from ..runtime import vault_state

router = APIRouter(prefix="/api/media", tags=["media"])

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
    for file in files:
        try:
            file_path = settings.UPLOAD_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type: mime_type = "application/octet-stream"
            
            stat = os.stat(file_path)
            new_media = models.Media(
                filename=file.filename,
                original_path=file.filename,
                media_type=mime_type,
                file_size=stat.st_size,
                is_encrypted=False
            )
            db.add(new_media)
            count += 1
        except Exception:
            continue
    db.commit()
    return {"status": "success", "count": count}

@router.post("/scan")
def trigger_scan(background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    background_tasks.add_task(scanner.scan_directory, db)
    return {"status": "scanning_started"}

@router.get("/{media_id}/content")
def get_media_content(media_id: int, db: Session = Depends(database.get_db)):
    media = get_media_item(db, media_id)
    
    if media.is_encrypted:
        if vault_state.get_key() is None:
            raise HTTPException(status_code=403, detail="Vault locked")
        file_path = settings.VAULT_DIR / Path(media.original_path).name
    else:
        file_path = settings.UPLOAD_DIR / Path(media.original_path).name

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(file_path, media_type=media.media_type)

@router.get("/{media_id}/thumbnail")
def get_media_thumbnail(media_id: int, db: Session = Depends(database.get_db)):
    media = get_media_item(db, media_id)
    if media.is_encrypted and vault_state.get_key() is None:
        raise HTTPException(status_code=403, detail="Vault locked")

    thumb_path = thumbnail.generate_thumbnail(media)
    if not thumb_path or not os.path.exists(thumb_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
        
    return FileResponse(thumb_path, media_type="image/jpeg")

@router.post("/bulk/encrypt")
def bulk_encrypt(ids: List[int], db: Session = Depends(database.get_db)):
    if vault_state.get_key() is None:
        raise HTTPException(status_code=403, detail="Vault locked")
        
    encrypted_count = 0
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media and not media.is_encrypted:
            filename = Path(media.original_path).name
            source_path = settings.UPLOAD_DIR / filename
            dest_path = settings.VAULT_DIR / filename
            
            if source_path.exists():
                try:
                    shutil.move(str(source_path), str(dest_path))
                    
                    if dest_path.exists() and not source_path.exists():
                        media.is_encrypted = True
                        encrypted_count += 1
                    elif dest_path.exists() and source_path.exists():
                        os.remove(source_path)
                        media.is_encrypted = True
                        encrypted_count += 1
                except Exception as e:
                    print(f"Encryption error for {filename}: {e}")
            else:
                print(f"Source file not found: {source_path}")

    db.commit()
    return {"status": "encrypted", "count": encrypted_count}

@router.post("/bulk/decrypt")
def bulk_decrypt(ids: List[int], db: Session = Depends(database.get_db)):
    if vault_state.get_key() is None:
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
                    shutil.move(str(source_path), str(dest_path))
                    
                    if dest_path.exists() and not source_path.exists():
                        media.is_encrypted = False
                        decrypted_count += 1
                    elif dest_path.exists() and source_path.exists():
                        os.remove(source_path)
                        media.is_encrypted = False
                        decrypted_count += 1
                except Exception as e:
                    print(f"Decryption error for {filename}: {e}")
            else:
                print(f"Vault file not found: {source_path}")

    db.commit()
    return {"status": "decrypted", "count": decrypted_count}

@router.post("/bulk/delete")
def bulk_delete(ids: List[int], db: Session = Depends(database.get_db)):
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media:
            try:
                filename = Path(media.original_path).name
                file_path = (settings.VAULT_DIR if media.is_encrypted else settings.UPLOAD_DIR) / filename
                
                if file_path.exists():
                    os.remove(file_path)
                
                thumb_path = settings.THUMBNAIL_DIR / f"thumb_{media.id}.jpg"
                if thumb_path.exists():
                    os.remove(thumb_path)
            except Exception as e:
                print(f"Delete error: {e}")
            db.delete(media)
    db.commit()
    return {"status": "deleted"}

@router.put("/bulk/album/{album_id}")
def set_album_for_media(album_id: int, ids: List[int], db: Session = Depends(database.get_db)):
    for mid in ids:
        media = db.query(models.Media).filter(models.Media.id == mid).first()
        if media:
            media.album_id = album_id
    db.commit()
    return {"status": "updated"}