import os
from pathlib import Path

class Settings:
    VERSION = "1.0.0"
    
    GITHUB_REPO_OWNER = "browensiz" 
    GITHUB_REPO_NAME = "HomeHub"   
    
    BASE_DIR = Path(__file__).resolve().parent
    ROOT_DIR = BASE_DIR.parent
    
    DATA_DIR = ROOT_DIR / "data"
    
    UPLOAD_DIR = DATA_DIR / "uploads"
    THUMBNAIL_DIR = DATA_DIR / "thumbnails"
    CACHE_DIR = DATA_DIR / "cache"
    UPDATE_DIR = ROOT_DIR / "update_stage"
    
    DATABASE_URL = f"sqlite:///{DATA_DIR}/homehub.db"
    
    SECRET_KEY = "temporary_secret_key_change_in_production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    def init_directories(self):
        for path in [self.DATA_DIR, self.UPLOAD_DIR, self.THUMBNAIL_DIR, self.CACHE_DIR]:
            path.mkdir(parents=True, exist_ok=True)

settings = Settings()