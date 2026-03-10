"""
MV photos to dir
Author: Gerardo Galvan
Created: 2026-03-10
Description: A simple script to move all photos in directory to year/month folders.
"""
import os
import shutil
from datetime import datetime
from PIL import Image
from pillow_heif import register_heif_opener
from tqdm.rich import tqdm

# Enable HEIC support
register_heif_opener()

SOURCE_DIR = os.path.expanduser("/photos")
TARGET_BASE = os.path.expanduser("/photos/test")

def get_accurate_date(path):
    try:
        with Image.open(path) as img:
            exif_data = img.getexif()
            if exif_data:
                for tag in [36867, 306]:
                    date_str = exif_data.get(tag)
                    if date_str:
                        return datetime.strptime(str(date_str).strip('\x00').strip(), '%Y:%m:%d %H:%M:%S')
    except Exception:
        pass
    stat = os.stat(path)
    return datetime.fromtimestamp(stat.st_mtime)

# --- STEP 1: Count total files ---
print("🔍 Scanning for files...")
all_files = []
for root, _, files in os.walk(SOURCE_DIR):
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.heic', '.png', '.mov', '.mp4')):
            all_files.append(os.path.join(root, f))

if not all_files:
    print("No matching files found.")
    exit()

# --- STEP 2: Move files with progress bar ---
moved_count = 0
with tqdm(total=len(all_files), desc="[bold cyan]Organizing Photos[/bold cyan]", unit="file") as pbar:
    for file_path in all_files:
        filename = os.path.basename(file_path)
        date_obj = get_accurate_date(file_path)
        
        dest_dir = os.path.join(TARGET_BASE, date_obj.strftime('%Y'), date_obj.strftime('%m'))
        os.makedirs(dest_dir, exist_ok=True)
        
        dest_path = os.path.join(dest_dir, filename)
        
        if os.path.exists(dest_path) and os.path.abspath(file_path) != os.path.abspath(dest_path):
            base, ext = os.path.splitext(filename)
            dest_path = os.path.join(dest_dir, f"{base}_{datetime.now().strftime('%H%M%S')}{ext}")

        try:
            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                shutil.move(file_path, dest_path)
                moved_count += 1
        except Exception as e:
            tqdm.write(f"❌ Error moving {filename}: {e}")
        
        pbar.update(1)

# --- STEP 3: Delete Empty Directories ---
print("\n🧹 Cleaning up empty directories...")
# topdown=False is critical: it visits leaf nodes first
for root, dirs, files in os.walk(SOURCE_DIR, topdown=False):
    for name in dirs:
        dir_path = os.path.join(root, name)
        try:
            # os.rmdir only deletes a directory if it is completely empty
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
        except Exception as e:
            pass # Folder likely wasn't empty or was in use

print(f"✨ Finished! {moved_count} items moved and empty folders removed.")
