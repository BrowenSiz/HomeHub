from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MediaBase(BaseModel):
    filename: str
    media_type: str

class AlbumBase(BaseModel):
    name: str
    description: Optional[str] = None

class AlbumRef(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class Media(MediaBase):
    id: int
    original_path: Optional[str]
    thumbnail_path: Optional[str]
    created_at: datetime
    is_encrypted: bool
    album_id: Optional[int]
    album: Optional[AlbumRef] = None

    class Config:
        from_attributes = True

class AlbumSummary(AlbumBase):
    id: int
    created_at: datetime
    is_encrypted: bool
    media_count: int = 0
    cover_photo: Optional[str] = None

    class Config:
        from_attributes = True

class AlbumDetail(AlbumSummary):
    media_items: List[Media] = []

    class Config:
        from_attributes = True

class AlbumCreate(AlbumBase):
    pass

class MediaCreate(MediaBase):
    original_path: str
    file_size: int

class SetupRequest(BaseModel):
    master_password: str
    pin: str

class LoginRequest(BaseModel):
    pin: str

class ChangePinRequest(BaseModel):
    master_password: str
    new_pin: str

class SystemStats(BaseModel):
    total_files: int
    total_size_bytes: int
    is_setup: bool
    version: str