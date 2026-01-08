from fastapi import APIRouter, HTTPException
from ..services import updater
from ..config import settings
import os
import signal
import threading
import time

router = APIRouter(prefix="/api/system", tags=["system"])

_heartbeat_callback = None

def set_heartbeat_callback(cb):
    global _heartbeat_callback
    _heartbeat_callback = cb

@router.post("/heartbeat")
def heartbeat():
    if _heartbeat_callback:
        _heartbeat_callback()
    return {"status": "alive"}

@router.get("/version")
def get_version():
    return {"version": settings.VERSION}

@router.get("/updates/check")
def check_updates():
    info = updater.check_for_updates()
    if not info:
        return {"update_available": False} 
    return info

@router.post("/updates/install")
def install_update():
    info = updater.check_for_updates()
    if not info or not info['update_available']:
        raise HTTPException(status_code=400, detail="Нет доступных обновлений")
    
    success = updater.perform_update(info['download_url'])
    
    if success:
        def kill_server():
            time.sleep(2)
            print("Shutting down for update...")
            os.kill(os.getpid(), signal.SIGTERM)
            
        threading.Thread(target=kill_server).start()
        return {"status": "update_started", "message": "Сервер перезагружается для установки обновления..."}
    else:
        raise HTTPException(status_code=500, detail="Ошибка при скачивании обновления")