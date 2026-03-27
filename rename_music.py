import os
import hashlib
import json
import shutil

# Directories to scan
DIRS = ['bgmus', 'github_pages/bgmus']
JSON_PATH = 'github_pages/music.json'

# Creative Names List
NEW_NAMES = [
    "Blues_Runtime.mp3",
    "Code_Rhythm.mp3",
    "Digital_Heartbeat.mp3",
    "Syntax_Soul.mp3",
    "Binary_Blues.mp3",
    "Algorithm_Flow.mp3",
    "Logic_Loop.mp3",
    "Pixel_Pulse.mp3",
    "Server_Song.mp3",
    "Data_Drift.mp3",
    "Compiled_Love.mp3",
    "Git_Flow.mp3",
    "Null_Pointer.mp3",
    "Stack_Trace.mp3",
    "Cloud_Compute.mp3",
    "Neural_Net.mp3",
    "Cyber_Serenade.mp3",
    "Virtual_Vibe.mp3",
    "Cached_Memory.mp3",
    "System_Call.mp3",
    "Debug_Mode.mp3",
    "Async_Await.mp3"
]

def get_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def main():
    # 1. Map Content Hash -> New Name
    hash_to_name = {}
    name_idx = 0
    
    # Track all files to be renamed: (old_path, new_name)
    renames = []
    
    print("--- Planning Renames ---")
    
    for d in DIRS:
        if not os.path.exists(d):
            continue
            
        for f in os.listdir(d):
            if not f.endswith('.mp3'):
                continue
                
            old_path = os.path.join(d, f)
            file_hash = get_hash(old_path)
            
            if not file_hash:
                continue
                
            # Assign new name if this content hasn't been seen
            if file_hash not in hash_to_name:
                if name_idx < len(NEW_NAMES):
                    hash_to_name[file_hash] = NEW_NAMES[name_idx]
                    name_idx += 1
                else:
                    # Fallback if we run out of creative names
                    hash_to_name[file_hash] = f"Blues_Track_{name_idx}.mp3"
                    name_idx += 1
            
            new_name = hash_to_name[file_hash]
            renames.append((old_path, os.path.join(d, new_name)))
            print(f"Plan: {f} -> {new_name}")

    # 2. Execute Renames
    print("\n--- Executing Renames ---")
    for old_path, new_path in renames:
        if old_path == new_path:
            continue
            
        try:
            os.rename(old_path, new_path)
            print(f"Renamed: {old_path} -> {new_path}")
        except OSError as e:
            print(f"Error renaming {old_path}: {e}")

    # 3. Update music.json
    print("\n--- Updating music.json ---")
    if os.path.exists(JSON_PATH):
        try:
            # We only care about files in github_pages/bgmus for the json
            # We can just list the directory now, as they are already renamed
            live_files = []
            if os.path.exists('github_pages/bgmus'):
                for f in os.listdir('github_pages/bgmus'):
                    if f.endswith('.mp3'):
                        # The json format expects "bgmus/filename.mp3"
                        live_files.append(f"bgmus/{f}")
            
            # Sort for neatness
            live_files.sort()
            
            with open(JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(live_files, f, indent=4)
                
            print(f"Updated {JSON_PATH} with {len(live_files)} tracks.")
            
        except Exception as e:
            print(f"Failed to update music.json: {e}")
    else:
        print(f"Warning: {JSON_PATH} not found.")

if __name__ == "__main__":
    main()
