from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import database, models
from .. import schemas, crypto_utils
from ..runtime import vault_state
from ..config import settings
import os
import shutil

router = APIRouter(prefix="/api/auth", tags=["auth"])

def secure_wipe_cache():
    try:
        if settings.CACHE_DIR.exists():
            for item in settings.CACHE_DIR.iterdir():
                if item.is_file():
                    try:
                        os.unlink(item)
                    except Exception:
                        pass
    except Exception as e:
        print(f"Cache wipe error: {e}")

@router.get("/status")
def get_auth_status(db: Session = Depends(database.get_db)):
    config = db.query(models.SystemConfig).first()
    is_open = vault_state.get_key() is not None
    return {
        "is_setup": bool(config and config.is_setup_complete),
        "is_vault_unlocked": is_open
    }

@router.get("/stats", response_model=schemas.SystemStats)
def get_system_stats(db: Session = Depends(database.get_db)):
    config = db.query(models.SystemConfig).first()
    total_files = db.query(models.Media).count()
    media_items = db.query(models.Media).with_entities(models.Media.file_size).all()
    total_size = sum(item.file_size for item in media_items) if media_items else 0

    return {
        "total_files": total_files,
        "total_size_bytes": total_size,
        "is_setup": bool(config and config.is_setup_complete),
        "version": "1.0.0 (Beta)"
    }

@router.post("/setup")
def setup_security(data: schemas.SetupRequest, db: Session = Depends(database.get_db)):
    config = db.query(models.SystemConfig).first()
    if config and config.is_setup_complete:
        raise HTTPException(status_code=400, detail="Система уже настроена")

    if not config:
        config = models.SystemConfig()
        db.add(config)

    master_key = crypto_utils.generate_master_key()

    config.master_password_hash = crypto_utils.get_password_hash(data.master_password)
    salt_mp = crypto_utils.generate_salt()
    key_mp = crypto_utils.derive_key_from_password(data.master_password, salt_mp)
    config.salt_mp = salt_mp
    config.encrypted_mk_by_mp = crypto_utils.encrypt_data(master_key, key_mp)

    salt_pin = crypto_utils.generate_salt()
    key_pin = crypto_utils.derive_key_from_password(data.pin, salt_pin)
    config.salt_pin = salt_pin
    config.encrypted_mk_by_pin = crypto_utils.encrypt_data(master_key, key_pin)
    
    config.is_setup_complete = True
    db.commit()
    
    vault_state.set_key(master_key)
    return {"status": "success"}

@router.post("/login")
def login_with_pin(data: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    config = db.query(models.SystemConfig).first()
    if not config or not config.is_setup_complete:
        raise HTTPException(status_code=400, detail="Система не настроена")

    try:
        key_from_pin = crypto_utils.derive_key_from_password(data.pin, config.salt_pin)
        master_key = crypto_utils.decrypt_data(config.encrypted_mk_by_pin, key_from_pin)
        
        if master_key is None:
            raise ValueError("Decryption failed")
            
        vault_state.set_key(master_key)
        return {"status": "success", "token": "session_active"}
        
    except Exception:
        raise HTTPException(status_code=401, detail="Неверный PIN код")

@router.post("/change-pin")
def change_pin(data: schemas.ChangePinRequest, db: Session = Depends(database.get_db)):
    config = db.query(models.SystemConfig).first()
    if not config or not config.is_setup_complete:
        raise HTTPException(status_code=400, detail="Система не настроена")

    if not crypto_utils.verify_password(data.master_password, config.master_password_hash):
        raise HTTPException(status_code=401, detail="Неверный Мастер-пароль")

    try:
        key_mp = crypto_utils.derive_key_from_password(data.master_password, config.salt_mp)
        master_key = crypto_utils.decrypt_data(config.encrypted_mk_by_mp, key_mp)
        
        if master_key is None:
            raise ValueError("Crypto failure")
    except Exception:
        raise HTTPException(status_code=500, detail="Ошибка восстановления ключей")

    new_salt_pin = crypto_utils.generate_salt()
    new_key_pin = crypto_utils.derive_key_from_password(data.new_pin, new_salt_pin)
    new_encrypted_mk = crypto_utils.encrypt_data(master_key, new_key_pin)

    config.salt_pin = new_salt_pin
    config.encrypted_mk_by_pin = new_encrypted_mk
    db.commit()

    return {"status": "success", "message": "PIN код успешно изменен"}

@router.post("/lock")
def lock_vault():
    vault_state.clear()
    secure_wipe_cache()
    return {"status": "locked"}