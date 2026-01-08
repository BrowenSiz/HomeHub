from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth, albums, media, system
from .database import database
import uvicorn
import os

# Инициализация
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

app.include_router(auth.router)
app.include_router(albums.router)
app.include_router(media.router)
app.include_router(system.router)

app.mount("/thumbnails", StaticFiles(directory=settings.THUMBNAIL_DIR), name="thumbnails")

# --- РАЗДАЧА FRONTEND ---
FRONTEND_DIR = settings.BASE_DIR / "static"

if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        if full_path.startswith("api") or full_path.startswith("thumbnails"):
            return {"detail": "Not Found"}, 404
            
        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"detail": "Frontend not found. Run 'npm run build' and copy dist to backend/static"}, 404

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False) 