import sys
import os
from pathlib import Path
import threading
import time
import socket

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import webview

from .config import settings
from .routers import auth, albums, media, system
from .services import updater 
from .database import database

updater.cleanup_old_versions()

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

if STATIC_DIR.exists():
    if ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api") or full_path.startswith("thumbnails"):
             return JSONResponse({"detail": "Not Found"}, status_code=404)
        
        file_path = STATIC_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return JSONResponse({"detail": "Frontend index.html not found"}, status_code=404)
else:
    @app.get("/")
    def root():
        return {"message": "HomeHub Backend Running", "mode": "Headless"}

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def check_server_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def init_window(window):
    server_ready = False
    for i in range(30):
        if check_server_port("127.0.0.1", 8000):
            server_ready = True
            break
        time.sleep(0.5)
    
    if server_ready:
        window.load_url("http://127.0.0.1:8000")
    else:
        window.load_html("<h1>Error: Server unreachable</h1>")

def on_closed():
    os._exit(0)

def get_icon_path():
    icon_name = "favicon.ico"
    if is_frozen:
        return str(Path(sys._MEIPASS) / "static" / icon_name)
    else:
        return str(Path(__file__).parent.parent / "frontend" / "public" / icon_name)

def start_app():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    loading_html = """
    <!DOCTYPE html>
    <html style="background: #0f172a;">
    <head><style>
        body { display: flex; justify-content: center; align-items: center; height: 100vh; color: white; font-family: sans-serif; }
        .loader { width: 48px; height: 48px; border: 3px solid #3b82f6; border-radius: 50%; border-bottom-color: transparent; animation: rot 1s linear infinite; }
        @keyframes rot { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style></head>
    <body><div><div class="loader"></div><div style="margin-top:20px">HOMEHUB</div></div></body>
    </html>
    """

    window = webview.create_window(
        title="HomeHub", 
        html=loading_html,
        width=1280, 
        height=850,
        min_size=(1000, 700),
        background_color='#0f172a',
        resizable=True
    )
    
    icon = get_icon_path()
    webview.start(init_window, window, icon=icon)

if __name__ == "__main__":
    start_app()