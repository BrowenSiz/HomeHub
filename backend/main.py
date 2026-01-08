import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import webbrowser
import threading
import time
import signal

from .config import settings
from .routers import auth, albums, media, system
from .database import database

settings.init_directories()
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="HomeHub", version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}

app.include_router(auth.router)
app.include_router(albums.router)
app.include_router(media.router)
app.include_router(system.router)

settings.THUMBNAIL_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/thumbnails", StaticFiles(directory=settings.THUMBNAIL_DIR), name="thumbnails")

is_frozen = getattr(sys, 'frozen', False)
if is_frozen:
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    BUNDLE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BUNDLE_DIR / "static"
ASSETS_DIR = STATIC_DIR / "assets"

last_heartbeat_time = time.time()
shutdown_event = threading.Event()

def heartbeat_monitor():
    time.sleep(60)
    while not shutdown_event.is_set():
        if time.time() - last_heartbeat_time > 10:
             os.kill(os.getpid(), signal.SIGTERM)
             break
        time.sleep(2)

def update_heartbeat():
    global last_heartbeat_time
    last_heartbeat_time = time.time()

system.set_heartbeat_callback(update_heartbeat)

def open_browser():
    time.sleep(1.5)
    if is_frozen:
        webbrowser.open("http://127.0.0.1:8000")

if STATIC_DIR.exists() and ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api") or full_path.startswith("thumbnails"):
             return JSONResponse({"detail": "Not Found"}, status_code=404)
        
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return JSONResponse({"detail": "Frontend index.html not found"}, status_code=404)
else:
    @app.get("/")
    def root():
        return {"message": "HomeHub API Running (Dev Mode)", "note": "Frontend not found"}

def start_app():
    threading.Thread(target=heartbeat_monitor, daemon=True).start()
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

if __name__ == "__main__":
    start_app()