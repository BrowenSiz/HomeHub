from fastapi import APIRouter, HTTPException
from ..services import updater
from ..config import settings
import os
import signal
import threading
import time

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/version")
def get_version():
    return {"version": settings.VERSION}

@router.get("/updates/check")
def check_updates():
    info = updater.check_for_updates()
    if not info:
        raise HTTPException(status_code=503, detail="Не удалось проверить обновления")
    return info

@router.post("/updates/install")
def install_update():
    info = updater.check_for_updates()
    if not info or not info['update_available']:
        raise HTTPException(status_code=400, detail="Нет доступных обновлений")
    
    success = updater.perform_update(info['download_url'])
    
    if success:
        def kill_server():
            time.sleep(1)
            print("Shutting down for update...")
            os.kill(os.getpid(), signal.SIGTERM)
            
        threading.Thread(target=kill_server).start()
        return {"status": "update_started", "message": "Сервер перезагружается для установки обновления..."}
    else:
        raise HTTPException(status_code=500, detail="Ошибка при скачивании обновления")