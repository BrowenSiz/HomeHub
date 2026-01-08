import os
import sys
from pathlib import Path

class Settings:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.ROOT_DIR = Path(sys.executable).parent
        else:
            self.ROOT_DIR = Path(__file__).resolve().parent.parent

        self.DATA_DIR = self.ROOT_DIR / "data"
        self.UPLOAD_DIR = self.DATA_DIR / "uploads"
        self.VAULT_DIR = self.DATA_DIR / "vault_storage" 
        self.THUMBNAIL_DIR = self.DATA_DIR / "thumbnails"
        self.CACHE_DIR = self.DATA_DIR / "cache"
        self.UPDATE_DIR = self.ROOT_DIR / "update_stage"
        
        self.DATABASE_URL = f"sqlite:///{self.DATA_DIR}/homehub.db"
        
        self.SECRET_KEY = "prod_secret_key"
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        self.VERSION = "1.0.0"
        self.GITHUB_REPO_OWNER = "BrowenSiz"
        self.GITHUB_REPO_NAME = "HomeHub"

    def init_directories(self):
        for path in [self.DATA_DIR, self.UPLOAD_DIR, self.VAULT_DIR, self.THUMBNAIL_DIR, self.CACHE_DIR]:
            path.mkdir(parents=True, exist_ok=True)

settings = Settings()