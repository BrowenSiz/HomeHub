from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class MediaType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"

class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    is_setup_complete = Column(Boolean, default=False)
    
    master_password_hash = Column(String, nullable=True)
    
    encrypted_mk_by_mp = Column(LargeBinary, nullable=True)
    salt_mp = Column(LargeBinary, nullable=True)
    
    encrypted_mk_by_pin = Column(LargeBinary, nullable=True)
    salt_pin = Column(LargeBinary, nullable=True)

class Album(Base):
    __tablename__ = "albums"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    is_encrypted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    media_items = relationship("Media", back_populates="album")

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    original_path = Column(String, unique=True, index=True)
    file_size = Column(Integer)
    media_type = Column(String)
    thumbnail_path = Column(String, nullable=True)
    
    is_encrypted = Column(Boolean, default=False)
    encrypted_filename = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    album_id = Column(Integer, ForeignKey("albums.id"), nullable=True)

    album = relationship("Album", back_populates="media_items")