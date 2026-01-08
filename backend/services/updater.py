import requests
import zipfile
import shutil
import os
import sys
from pathlib import Path
from ..config import settings

def check_for_updates():
    url = f"https://api.github.com/repos/{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}/releases/latest"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data['tag_name'].lstrip('v')
            current_version = settings.VERSION
            
            update_available = latest_version != current_version
            
            return {
                "current_version": current_version,
                "latest_version": latest_version,
                "update_available": update_available,
                "download_url": data['zipball_url'],
                "release_notes": data['body']
            }
        return None
    except Exception as e:
        print(f"Update check failed: {e}")
        return None

def perform_update(download_url: str):
    if settings.UPDATE_DIR.exists():
        shutil.rmtree(settings.UPDATE_DIR)
    settings.UPDATE_DIR.mkdir()

    zip_path = settings.UPDATE_DIR / "update.zip"

    try:
        print(f"Downloading update from {download_url}...")
        response = requests.get(download_url, stream=True)
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print("Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(settings.UPDATE_DIR)
        
        extracted_root = next(settings.UPDATE_DIR.iterdir())
        if extracted_root.is_dir():
            for item in extracted_root.iterdir():
                shutil.move(str(item), str(settings.UPDATE_DIR))
            extracted_root.rmdir()
        
        os.remove(zip_path)

        with open(settings.ROOT_DIR / ".update_ready", "w") as f:
            f.write("ready")

        print("Update prepared. Restarting...")
        return True

    except Exception as e:
        print(f"Update failed: {e}")
        return False