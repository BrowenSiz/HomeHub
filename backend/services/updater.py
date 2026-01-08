import os
import sys
import shutil
import requests
import zipfile
import tempfile
import subprocess
from pathlib import Path
from ..config import settings

def cleanup_old_versions():
    if getattr(sys, 'frozen', False):
        current_exe = Path(sys.executable)
        old_exe = current_exe.with_name(current_exe.name + ".old")
        
        if old_exe.exists():
            try:
                os.remove(old_exe)
                print(f"[Updater] Cleaned up old version: {old_exe}")
            except Exception as e:
                print(f"[Updater] Cleanup failed (will try next time): {e}")

def check_for_updates():
    try:
        url = f"https://api.github.com/repos/{settings.GITHUB_REPO_OWNER}/{settings.GITHUB_REPO_NAME}/releases/latest"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            latest_version = data['tag_name'].lstrip('v')
            
            if latest_version != settings.VERSION:
                download_url = None
                for asset in data['assets']:
                    if asset['name'].endswith('.zip') or asset['name'].endswith('.exe'):
                        download_url = asset['browser_download_url']
                        break
                
                return {
                    "update_available": True,
                    "latest_version": latest_version,
                    "current_version": settings.VERSION,
                    "download_url": download_url,
                    "release_notes": data['body']
                }
    except Exception as e:
        print(f"[Updater] Check failed: {e}")
    
    return {"update_available": False, "current_version": settings.VERSION}

def perform_update_in_place(download_url: str):
    if not getattr(sys, 'frozen', False):
        print("[Updater] Cannot update in development mode (not frozen).")
        return False

    try:
        current_exe = Path(sys.executable)
        exe_dir = current_exe.parent
        
        print(f"[Updater] Downloading from {download_url}...")
        resp = requests.get(download_url, stream=True)
        resp.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_file:
            for chunk in resp.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_zip_path = Path(tmp_file.name)

        new_exe_source = None
        extract_dir = Path(tempfile.gettempdir()) / "homehub_update_extract"
        if extract_dir.exists(): shutil.rmtree(extract_dir)
        extract_dir.mkdir()

        try:
            if download_url.endswith('.zip'):
                with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                found = list(extract_dir.rglob("HomeHub.exe"))
                if not found:
                    raise Exception("HomeHub.exe not found in update archive")
                new_exe_source = found[0]
            
            elif download_url.endswith('.exe'):
                new_exe_source = extract_dir / "HomeHub.exe"
                shutil.copy(tmp_zip_path, new_exe_source)
            
            old_exe_path = current_exe.with_name(current_exe.name + ".old")
            if old_exe_path.exists():
                os.remove(old_exe_path)
            
            os.rename(current_exe, old_exe_path)
            
            shutil.move(str(new_exe_source), str(current_exe))
            
            os.remove(tmp_zip_path)
            shutil.rmtree(extract_dir)
            
            return True

        except Exception as e:
            print(f"[Updater] Extraction/Swap failed: {e}")
            if 'old_exe_path' in locals() and old_exe_path.exists() and not current_exe.exists():
                os.rename(old_exe_path, current_exe)
            return False

    except Exception as e:
        print(f"[Updater] Update process failed: {e}")
        return False

def restart_application():
    if getattr(sys, 'frozen', False):
        subprocess.Popen([sys.executable])
        os._exit(0)