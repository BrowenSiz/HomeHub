import os
from pathlib import Path
from sqlalchemy.orm import Session
from ..config import settings
from ..database import models
from .thumbnail import generate_thumbnail

IMAGE_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif',
    '.heic', '.heif', 
    '.cr2', '.nef', '.dng', '.arw', '.orf', '.rw2', '.pef', '.srw'
}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'}

def scan_storage(db: Session):
    print("--- [Scanner] Запуск процесса сканирования ---")
    
    if not settings.UPLOAD_DIR.exists():
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    found_files = []
    
    root_dir = settings.UPLOAD_DIR
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.startswith('.'): continue
                
            path = Path(root) / file
            ext = path.suffix.lower()
            
            if ext in IMAGE_EXTENSIONS or ext in VIDEO_EXTENSIONS:
                found_files.append(path)

    print(f"--- [Scanner] Найдено файлов на диске: {len(found_files)}")

    count_new = 0
    count_updated = 0
    count_errors = 0
    
    for file_path in found_files:
        try:
            try:
                relative_path = str(file_path.relative_to(settings.UPLOAD_DIR))
            except ValueError:
                continue
            
            real_size = file_path.stat().st_size
            
            existing_media = db.query(models.Media).filter(models.Media.original_path == relative_path).first()
            
            ext = file_path.suffix.lower()
            media_type = models.MediaType.VIDEO if ext in VIDEO_EXTENSIONS else models.MediaType.PHOTO
            
            mime_type = "application/octet-stream"
            if ext in VIDEO_EXTENSIONS:
                mime_type = f"video/{ext.lstrip('.')}"
            elif ext in ['.jpg', '.jpeg']: mime_type = "image/jpeg"
            elif ext == '.png': mime_type = "image/png"
            elif ext == '.webp': mime_type = "image/webp"
            elif ext in ['.heic', '.heif']: mime_type = "image/heic"
            elif ext in ['.cr2', '.nef', '.dng', '.arw']: mime_type = f"image/x-{ext.lstrip('.')}"
            else: mime_type = f"image/{ext.lstrip('.')}"

            if not existing_media:
                print(f"--- [New] Новый файл: {relative_path}")
                
                thumb_filename = generate_thumbnail(file_path, file_path.name)

                new_media = models.Media(
                    filename=file_path.name,
                    original_path=relative_path,
                    file_size=real_size,
                    media_type=mime_type,
                    thumbnail_path=thumb_filename,
                    is_encrypted=False
                )
                db.add(new_media)
                count_new += 1
            
            else:
                needs_save = False
                
                if existing_media.file_size != real_size:
                    existing_media.file_size = real_size
                    needs_save = True
                
                if not existing_media.thumbnail_path:
                    print(f"--- Генерирую превью для: {relative_path}")
                    class TempMedia:
                        id = existing_media.id
                        original_path = relative_path
                        media_type = mime_type
                        is_encrypted = False
                    
                    thumb_filename = generate_thumbnail(TempMedia(), None)
                    if thumb_filename:
                        existing_media.thumbnail_path = Path(thumb_filename).name
                        needs_save = True
                
                if needs_save:
                    db.add(existing_media)
                    count_updated += 1
                
            if (count_new + count_updated) % 10 == 0:
                db.commit()
                    
        except Exception as e:
            print(f"--- [Scanner] Ошибка обработки файла {file_path}: {e}")
            count_errors += 1
            continue
            
    db.commit()
    print(f"--- [Scanner] Завершено. Добавлено: {count_new}, Обновлено: {count_updated}, Ошибок: {count_errors} ---")