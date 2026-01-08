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
        html_error = """
        <body style="background:#111; color:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh;">
            <div style="text-align:center">
                <h2 style="color:#ff5555">Ошибка запуска</h2>
                <p>Не удалось подключиться к серверу HomeHub.</p>
                <p style="opacity:0.5; font-size:0.8em">Попробуйте перезапустить приложение.</p>
            </div>
        </body>
        """
        window.load_html(html_error)

def on_closed():
    os._exit(0)

def start_app():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    loading_html = """
    <!DOCTYPE html>
    <html style="background: #0f172a;"> <!-- Цвет фона как у приложения -->
    <head>
        <style>
            body { 
                margin: 0; 
                display: flex; 
                justify-content: center; 
                align-items: center; 
                height: 100vh; 
                font-family: system-ui, -apple-system, sans-serif;
                color: white;
                user-select: none;
            }
            .loader {
                width: 48px;
                height: 48px;
                border: 3px solid #3b82f6;
                border-radius: 50%;
                display: inline-block;
                position: relative;
                box-sizing: border-box;
                animation: rotation 1s linear infinite;
            }
            .loader::after {
                content: '';  
                box-sizing: border-box;
                position: absolute;
                left: 50%;
                top: 50%;
                transform: translate(-50%, -50%);
                width: 40px;
                height: 40px;
                border-radius: 50%;
                border: 3px solid transparent;
                border-bottom-color: #ef4444;
                animation: rotation 1.5s linear infinite reverse;
            }
            @keyframes rotation {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div style="text-align: center;">
            <div class="loader"></div>
            <div style="margin-top: 20px; font-weight: 500; opacity: 0.7; letter-spacing: 1px;">HOMEHUB</div>
        </div>
    </body>
    </html>
    """

    window = webview.create_window(
        title="HomeHub", 
        html=loading_html,
        width=1280,
        height=850,
        min_size=(1000, 700),
        resizable=True,
        text_select=False,
        confirm_close=True,
        background_color='#0f172a'
    )
    
    webview.start(init_window, window)

if __name__ == "__main__":
    start_app()