from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from ..database import database, models
from ..services import updater
from ..config import settings
import threading
import time
import os
import shutil
import sys

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/version")
def get_version():
    return {"version": settings.VERSION}

@router.get("/stats")
def get_system_stats(db: Session = Depends(database.get_db)):
    try:
        total, used, free = shutil.disk_usage(settings.DATA_DIR)
    except:
        total, used, free = 0, 0, 0

    db_size = 0
    db_path = settings.DATA_DIR / "homehub.db"
    if db_path.exists():
        db_size = db_path.stat().st_size

    total_media = db.query(models.Media).count()
    encrypted_media = db.query(models.Media).filter(models.Media.is_encrypted == True).count()
    albums_count = db.query(models.Album).count()
    
    data_path = str(settings.DATA_DIR.absolute())

    return {
        "storage": {
            "total": total,
            "used": used,
            "free": free,
            "percent": round((used / total) * 100, 1) if total > 0 else 0
        },
        "app": {
            "db_size": db_size,
            "total_files": total_media,
            "encrypted_files": encrypted_media,
            "albums": albums_count
        },
        "paths": {
            "data_root": data_path
        }
    }

@router.get("/updates/check")
def check_updates():
    return updater.check_for_updates()

@router.post("/updates/install")
def install_update(background_tasks: BackgroundTasks):
    info = updater.check_for_updates()
    if not info or not info.get('update_available'):
        raise HTTPException(status_code=400, detail="No updates available")
    
    success = updater.perform_update_in_place(info['download_url'])
    
    if success:
        return {"status": "success", "message": "Обновление установлено. Перезапустите приложение."}
    else:
        raise HTTPException(status_code=500, detail="Ошибка установки обновления")

@router.post("/restart")
def restart_app():
    def _restart():
        time.sleep(1)
        updater.restart_application()
    
    threading.Thread(target=_restart).start()
    return {"status": "restarting"}

@router.post("/heartbeat")
def heartbeat():
    return {"status": "alive"}