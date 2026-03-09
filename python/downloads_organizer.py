import os
import shutil
from pathlib import Path
from datetime import datetime
from tqdm.rich import tqdm  

# --- CONFIGURATION ---
MOUNT_POINT = Path("/mnt/nas_downloads")
DOWNLOADS_PATH = MOUNT_POINT / "TEMP"

FILE_TYPES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xmlc", ".layout", ".xlsx"],
    "Images": [".jpg", ".jpeg", ".png", ".heic", ".gif"],
    "Books": [".epub"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Audio": [".mp3", ".flac", ".alac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"], # Removed duplicate .rar
    "Software": [".exe", ".rpm", ".app", ".dmg", ".pkg", ".msix", ".iso"],
    "Torrents": [".torrent", ".nzb"],
}

# Define the folders we want to IGNORE when searching
TARGET_FOLDERS = [DOWNLOADS_PATH / category for category in FILE_TYPES.keys()]
TARGET_FOLDERS.append(DOWNLOADS_PATH / "Other")

def organize_nas_downloads():
    if not os.path.ismount(MOUNT_POINT):
        print(f"❌ Error: NAS is not mounted at {MOUNT_POINT}!")
        return

    if not DOWNLOADS_PATH.exists():
        print(f"❌ Error: The target folder {DOWNLOADS_PATH} does not exist!")
        return

    print(f"🧹 Organizing NAS folder recursively: {DOWNLOADS_PATH}")

    # Gather all files, recursively, but ignore our organized category folders
    files_to_move = []
    for item in DOWNLOADS_PATH.rglob('*'):
        if item.is_file():
            # Check if this file is already inside one of the TARGET_FOLDERS
            if not any(target in item.parents for target in TARGET_FOLDERS):
                files_to_move.append(item)

    if not files_to_move:
        print("No new files found to organize.")
        return

    with tqdm(total=len(files_to_move), desc="🚀 Organizing Downloads", unit="file", colour="green") as pbar:
        for item in files_to_move:
            moved = False
            extension = item.suffix.lower()

            for category, extensions in FILE_TYPES.items():
                if extension in extensions:
                    dest_dir = DOWNLOADS_PATH / category
                    dest_dir.mkdir(exist_ok=True)
                    
                    # Handle name collisions
                    dest_file = dest_dir / item.name
                    if dest_file.exists():
                        ts = datetime.now().strftime("%H%M%S")
                        dest_file = dest_dir / f"{item.stem}_{ts}{item.suffix}"
                    
                    try:
                        shutil.move(str(item), str(dest_file))
                    except Exception as e:
                        tqdm.write(f"⚠️ Could not move {item.name}: {e}")
                    
                    moved = True
                    break
            
            if not moved:
                other_dir = DOWNLOADS_PATH / "Other"
                other_dir.mkdir(exist_ok=True)
                
                dest_file = other_dir / item.name
                if dest_file.exists():
                    ts = datetime.now().strftime("%H%M%S")
                    dest_file = other_dir / f"{item.stem}_{ts}{item.suffix}"

                try:
                    shutil.move(str(item), str(dest_file))
                except Exception as e:
                    tqdm.write(f"⚠️ Could not move {item.name}: {e}")

            pbar.update(1)

    print("\n✨ NAS TEMP folder is now organized!")

if __name__ == "__main__":
    organize_nas_downloads()
