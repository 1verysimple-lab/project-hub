import os
import subprocess
import json
import shutil
import glob
import hashlib
from datetime import datetime

# --- CONFIGURATION from hub_manager.py ---
SOURCE_DIR = "."
DEST_DIR = "github_pages"
PROJECTS_JSON = os.path.join(DEST_DIR, "projects.json")
MUSIC_SOURCE_DIR = "bgmus"
MUSIC_DEST_DIR = os.path.join(DEST_DIR, "bgmus")
MUSIC_JSON = os.path.join(DEST_DIR, "music.json")

TARGET_URL = "https://1verysimple-lab.github.io/project-hub/"
LOGO_HTML = f"""
<!-- BLUES HUB NAVIGATION -->
<a href="{TARGET_URL}" 
   target="_blank"
   style="position: fixed; top: 20px; left: 20px; z-index: 9999; display: flex; align-items: center; gap: 8px; padding: 8px 12px; background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(8px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; text-decoration: none; color: #e2e8f0; font-family: system-ui, sans-serif; font-size: 13px; font-weight: 500; transition: all 0.2s ease; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
   onmouseover="this.style.transform='translateY(-1px)'; this.style.background='rgba(15, 23, 42, 0.95)'"
   onmouseout="this.style.transform='translateY(0)'; this.style.background='rgba(15, 23, 42, 0.8)'">
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="7" x="3" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="14" rx="1"></rect><rect width="7" height="7" x="3" y="14" rx="1"></rect></svg>
    <span>Hub</span>
</a>
<!-- END BLUES HUB NAVIGATION -->
"""

# --- BACKEND LOGIC (Relevant parts from HubBackend) ---

class HubBackendMinimal:
    def __init__(self):
        self.ensure_dirs()

    def ensure_dirs(self):
        if not os.path.exists(DEST_DIR):
            os.makedirs(DEST_DIR)
        if not os.path.exists(MUSIC_DEST_DIR):
            os.makedirs(MUSIC_DEST_DIR)

    def load_projects(self):
        if not os.path.exists(PROJECTS_JSON):
            return []
        try:
            with open(PROJECTS_JSON, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save_projects(self, data):
        with open(PROJECTS_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def get_file_hash(self, filepath):
        if not os.path.exists(filepath):
            return None
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def sync_all(self, log_callback):
        log_callback("Starting Full Sync...")
        self._sync_music(log_callback)
        self._sync_assets(log_callback)
        self._sync_projects(log_callback)
        log_callback("Sync Complete.")

    def _sync_music(self, log_callback):
        if not os.path.exists(MUSIC_SOURCE_DIR): return
        src_files = glob.glob(os.path.join(MUSIC_SOURCE_DIR, "*.mp3"))
        src_names = [os.path.basename(f) for f in src_files]
        dest_files = glob.glob(os.path.join(MUSIC_DEST_DIR, "*.mp3"))
        dest_names = [os.path.basename(f) for f in dest_files]
        
        for f in dest_names:
            if f not in src_names:
                os.remove(os.path.join(MUSIC_DEST_DIR, f))
                log_callback(f"[Music] Deleted {f}")
        for f in src_names:
            src = os.path.join(MUSIC_SOURCE_DIR, f)
            dst = os.path.join(MUSIC_DEST_DIR, f)
            if self._needs_update(src, dst):
                shutil.copy2(src, dst)
                log_callback(f"[Music] Synced {f}")
        
        track_list = [f"bgmus/{n}" for n in sorted(src_names)]
        with open(MUSIC_JSON, 'w', encoding='utf-8') as f:
            json.dump(track_list, f, indent=4)

    def _sync_assets(self, log_callback):
        exts = ['*.webp', '*.png', '*.jpg', '*.jpeg', '*.svg', '*.gif', '*.wav']
        for ext in exts:
            for src in glob.glob(ext):
                fname = os.path.basename(src)
                dst = os.path.join(DEST_DIR, fname)
                if self._needs_update(src, dst):
                    shutil.copy2(src, dst)
                    log_callback(f"[Asset] Synced {fname}")

    def _sync_projects(self, log_callback):
        projects = self.load_projects()
        for p in projects:
            rel_path = p['filename']
            if "/" in rel_path or "" in rel_path:
                folder_name = os.path.dirname(rel_path)
                src_folder = os.path.join(SOURCE_DIR, folder_name)
                dst_folder = os.path.join(DEST_DIR, folder_name)
                
                if os.path.exists(src_folder):
                    if not os.path.exists(dst_folder): os.makedirs(dst_folder)
                    for root, dirs, files in os.walk(src_folder):
                        rel_root = os.path.relpath(root, src_folder)
                        cur_dst_root = os.path.join(dst_folder, rel_root)
                        if not os.path.exists(cur_dst_root): os.makedirs(cur_dst_root)
                        for file in files:
                            s = os.path.join(root, file)
                            d = os.path.join(cur_dst_root, file)
                            if self._needs_update(s, d):
                                shutil.copy2(s, d)
                                log_callback(f"[Project] Updated file {file} in {folder_name}")
                else:
                    log_callback(f"[Warning] Source folder missing for {rel_path}")
            else:
                src_path = os.path.join(SOURCE_DIR, rel_path)
                dst_path = os.path.join(DEST_DIR, rel_path)
                if os.path.exists(src_path):
                    if self._needs_update(src_path, dst_path):
                        shutil.copy2(src_path, dst_path)
                        log_callback(f"[Project] Synced {rel_path}")
                else:
                    log_callback(f"[Warning] Source file missing: {rel_path}")

    def _needs_update(self, src, dst):
        if not os.path.exists(dst): return True
        return self.get_file_hash(src) != self.get_file_hash(dst)

    def git_deploy(self, message, log_callback):
        original_dir = os.getcwd()
        try:
            os.chdir(DEST_DIR)
            log_callback("---")
            
            # Need to stage changes first to see if there's anything to commit
            subprocess.run("git add .", shell=True, check=True)

            res = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
            if not res.stdout.strip():
                log_callback("No changes to push.")
                return

            log_callback("Staging changes...")
            # subprocess.run("git add .", shell=True, check=True) # Already staged
            log_callback(f"Committing: {message}")
            subprocess.run(f'git commit -m "{message}"', shell=True, check=True)
            log_callback("Pulling (Rebase)...")
            subprocess.run("git pull --rebase", shell=True, check=True)
            log_callback("Pushing to GitHub...")
            subprocess.run("git push", shell=True, check=True)
            log_callback("SUCCESS: Deployed to GitHub Pages.")
        except Exception as e:
            log_callback(f"ERROR: {e}")
        finally:
            os.chdir(original_dir)

def main():
    backend = HubBackendMinimal()

    def log_message(message):
        print(message)
    
    print("\nStarting sync and deploy for updated Cambermap...")
    backend.sync_all(log_message)
    backend.git_deploy("Update Camber Sands map content", log_message)
    
    print("\nProcess complete.")

if __name__ == "__main__":
    main()
