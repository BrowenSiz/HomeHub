from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..services import updater
from ..config import settings
import threading
import time
import os
import sys

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/version")
def get_version():
    return {"version": settings.VERSION}

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