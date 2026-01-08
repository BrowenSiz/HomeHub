from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import database, models
from .. import schemas

router = APIRouter(prefix="/api/albums", tags=["albums"])

@router.get("/", response_model=List[schemas.AlbumSummary])
def read_albums(db: Session = Depends(database.get_db)):
    albums = db.query(models.Album).all()
    
    result = []
    for album in albums:
        media_count = db.query(models.Media).filter(
            models.Media.album_id == album.id,
            models.Media.is_encrypted == False
        ).count()
        
        cover = db.query(models.Media).filter(
            models.Media.album_id == album.id,
            models.Media.is_encrypted == False,
            models.Media.thumbnail_path != None
        ).order_by(models.Media.created_at.desc()).first()

        album_data = schemas.AlbumSummary(
            id=album.id,
            name=album.name,
            description=album.description,
            created_at=album.created_at,
            is_encrypted=album.is_encrypted,
            media_count=media_count,
            cover_photo=cover.thumbnail_path if cover else None
        )
        result.append(album_data)
        
    return result

@router.get("/{album_id}", response_model=schemas.AlbumDetail)
def read_album_details(album_id: int, db: Session = Depends(database.get_db)):
    album = db.query(models.Album).filter(models.Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Альбом не найден")
    
    media_items = db.query(models.Media).filter(
        models.Media.album_id == album.id,
        models.Media.is_encrypted == False
    ).order_by(models.Media.created_at.desc()).all()

    album.media_items = media_items
    # media_count и cover заполнятся автоматически или можно пропустить для detail
    return album

@router.post("/", response_model=schemas.AlbumSummary)
def create_album(album: schemas.AlbumCreate, db: Session = Depends(database.get_db)):
    db_album = models.Album(name=album.name, description=album.description)
    db.add(db_album)
    db.commit()
    db.refresh(db_album)
    return schemas.AlbumSummary.model_validate(db_album)

@router.delete("/{album_id}")
def delete_album(album_id: int, db: Session = Depends(database.get_db)):
    album = db.query(models.Album).filter(models.Album.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Альбом не найден")
    
    # Отвязываем фото
    db.query(models.Media).filter(models.Media.album_id == album_id).update({"album_id": None})
    
    db.delete(album)
    db.commit()
    return {"status": "success", "message": "Альбом удален, фото сохранены в библиотеке"}