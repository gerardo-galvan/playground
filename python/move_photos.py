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
# Import from tqdm.rich instead of tqdm
from tqdm.rich import tqdm

# Enable HEIC support
register_heif_opener()

SOURCE_DIR = os.path.expanduser("/Photos")
TARGET_BASE = os.path.expanduser("/Photos")

def get_accurate_date(path):
    try:
        with Image.open(path) as img:
            exif_data = img.getexif()
            if exif_data:
                # 36867 = DateTimeOriginal, 306 = DateTime
                for tag in [36867, 306]:
                    date_str = exif_data.get(tag)
                    if date_str:
                        # Some EXIF dates have trailing null bytes or extra spaces
                        return datetime.strptime(str(date_str).strip('\x00').strip(), '%Y:%m:%d %H:%M:%S')
    except Exception:
        pass
    
    # Fallback: using the file modification time
    stat = os.stat(path)
    return datetime.fromtimestamp(stat.st_mtime)

# --- STEP 1: Count total files ---
# We use a list comprehension for a cleaner look
print("🔍 Scanning for photos and videos...")
all_files = [
    os.path.join(root, f) 
    for root, _, files in os.walk(SOURCE_DIR) 
    for f in files if f.lower().endswith(('.jpg', '.jpeg', '.heic', '.png', '.mov', '.mp4'))
]

if not all_files:
    print("No matching files found. Check your SOURCE_DIR.")
    exit()

# --- STEP 2: Move files with rich progress bar ---
moved_count = 0

# The rich progress bar automatically handles the layout
with tqdm(total=len(all_files), desc="[bold magenta]Organizing Photos[/bold magenta]", unit="file") as pbar:
    for file_path in all_files:
        filename = os.path.basename(file_path)
        
        # Don't try to move a file into a subfolder of itself (prevents infinite loops)
        if "Organized_Photos" in file_path:
            pbar.update(1)
            continue
            
        date_obj = get_accurate_date(file_path)
        
        # Structure: Year / Month
        dest_dir = os.path.join(TARGET_BASE, date_obj.strftime('%Y'), date_obj.strftime('%m'))
        os.makedirs(dest_dir, exist_ok=True)
        
        dest_path = os.path.join(dest_dir, filename)
        
        # Handle duplicate filenames in the destination
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(filename)
            dest_path = os.path.join(dest_dir, f"{base}_{datetime.now().strftime('%H%M%S')}{ext}")

        try:
            # Check if source and dest are the same to avoid errors
            if os.path.abspath(file_path) != os.path.abspath(dest_path):
                shutil.move(file_path, dest_path)
                moved_count += 1
        except Exception as e:
            # tqdm.write ensures the error message doesn't break the progress bar layout
            tqdm.write(f"❌ Error moving {filename}: {e}")
        
        pbar.update(1)

print(f"\n✨ Finished! {moved_count} items organized into folders.")
