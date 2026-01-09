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

try:
    updater.cleanup_old_versions()
except:
    pass

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

# Static Files
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
    # Wait for server
    for i in range(30):
        if check_server_port("127.0.0.1", 8000):
            window.load_url("http://127.0.0.1:8000")
            return
        time.sleep(0.5)
    
    window.load_html("<h1 style='color:white; font-family:sans-serif'>Server Timeout</h1>")

def get_icon_path():
    icon_name = "favicon.ico"
    if is_frozen:
        icon_path = Path(sys._MEIPASS) / "static" / icon_name
        if icon_path.exists(): return str(icon_path)
    else:
        dev_path = Path(__file__).resolve().parent.parent / "frontend" / "public" / icon_name
        if dev_path.exists(): return str(dev_path)
    return None

def start_app():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    loading_html = """
    <!DOCTYPE html>
    <html style="background: #0f172a; color: white; font-family: sans-serif;">
    <head><style>
        body { margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .loader { width: 50px; height: 50px; border: 3px solid #3b82f6; border-top-color: transparent; border-radius: 50%; animation: s 1s linear infinite; }
        @keyframes s { to { transform: rotate(360deg); } }
    </style></head>
    <body>
        <div style="text-align:center">
            <div class="loader"></div>
            <p style="margin-top:20px; opacity:0.7">STARTING...</p>
        </div>
    </body>
    </html>
    """

    icon_path = get_icon_path()

    window = webview.create_window(
        title="HomeHub", 
        html=loading_html,
        width=1280, 
        height=850,
        min_size=(1000, 700),
        background_color='#0f172a',
        resizable=True,
        frameless=False,
        easy_drag=False
    )
    
    webview.start(init_window, window, gui='edgechromium', debug=False)

if __name__ == "__main__":
    start_app()