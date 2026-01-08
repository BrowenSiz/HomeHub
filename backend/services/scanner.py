import os
from pathlib import Path
from sqlalchemy.orm import Session
from ..config import settings
from ..database import models
from .thumbnail import generate_thumbnail

# Поддерживаемые форматы файлов
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.cr2', '.nef', '.dng', '.arw', '.bmp', '.tiff'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

def scan_storage(db: Session):
    print("--- [Scanner] Запуск процесса сканирования ---")
    
    if not settings.PUBLIC_DIR.exists():
        print(f"--- [Scanner] Папка {settings.PUBLIC_DIR} не найдена. Создаю...")
        settings.PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

    found_files = []
    
    # 1. Рекурсивный поиск файлов на диске
    for root, _, files in os.walk(settings.PUBLIC_DIR):
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
    
    # 2. Обработка списка файлов
    for file_path in found_files:
        try:
            try:
                relative_path = str(file_path.relative_to(settings.STORAGE_DIR))
            except ValueError:
                continue
            
            # Получаем реальный размер с диска
            real_size = file_path.stat().st_size
            
            # Проверяем по базе
            existing_media = db.query(models.Media).filter(models.Media.original_path == relative_path).first()
            
            # Если файла нет в базе - добавляем
            if not existing_media:
                print(f"--- [New] Новый файл: {file_path.name}")
                ext = file_path.suffix.lower()
                media_type = models.MediaType.VIDEO if ext in VIDEO_EXTENSIONS else models.MediaType.PHOTO
                thumb_filename = generate_thumbnail(file_path, file_path.name)

                new_media = models.Media(
                    filename=file_path.name,
                    original_path=relative_path,
                    file_size=real_size,
                    media_type=media_type,
                    thumbnail_path=thumb_filename,
                    is_encrypted=False
                )
                db.add(new_media)
                count_new += 1
            
            else:
                needs_save = False
                
                # 1. Если нет размера или он 0
                if not existing_media.file_size or existing_media.file_size == 0:
                    print(f"--- Обновляю размер файла для: {file_path.name}")
                    existing_media.file_size = real_size
                    needs_save = True
                
                # 2. Если превью нет
                if not existing_media.thumbnail_path:
                    print(f"--- Генерирую превью для: {file_path.name}")
                    thumb_filename = generate_thumbnail(file_path, file_path.name)
                    if thumb_filename:
                        existing_media.thumbnail_path = thumb_filename
                        needs_save = True
                
                if needs_save:
                    db.add(existing_media)
                    count_updated += 1
                
            if (count_new + count_updated) % 10 == 0 and (count_new + count_updated) > 0:
                db.commit()
                    
        except Exception as e:
            print(f"--- [Scanner] Ошибка обработки файла {file_path.name}: {e}")
            count_errors += 1
            continue
            
    db.commit()
    print(f"--- [Scanner] Завершено. Добавлено: {count_new}, Исправлено: {count_updated}, Ошибок: {count_errors} ---")