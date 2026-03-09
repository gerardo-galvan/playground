import os
import shutil
from pathlib import Path
from datetime import datetime
import exiftool  # pip install pyexiftool
from tqdm.rich import tqdm  # pip install tqdm rich

# --- DYNAMIC CONFIGURATION ---
if os.name == 'nt':  # Windows
    BASE_DIR = Path("G:/Files/Photos/Import")
else:  # RHEL 10
    BASE_DIR = Path("/home/g/Pictures/temp")

# Destination Roots
DOWNLOADS_ROOT = BASE_DIR / "Downloads"
APPLE_PHOTOS_ROOT = BASE_DIR / "iPhone"

def organize_media():
    with exiftool.ExifToolHelper() as et:
        print(f"🔍 Scanning: {BASE_DIR}")
        
        all_files = [f for f in BASE_DIR.rglob('*') 
                     if f.is_file() 
                     and DOWNLOADS_ROOT not in f.parents 
                     and APPLE_PHOTOS_ROOT not in f.parents]
        
        if not all_files:
            print("No new files found to organize.")
            return

        # Ensure this block stays INSIDE the exiftool block so 'et' stays open
        with tqdm(total=len(all_files), desc="🚀 Organizing Library", unit="file", colour="green") as pbar:
            for file_path in all_files:
                try:
                    metadata = et.get_metadata(str(file_path))[0]
                    
                    # IMPROVED CHECK: Look for 'Apple' in any 'Make' tag (EXIF, QuickTime, etc.)
                    is_apple = any("Apple" in str(v) for k, v in metadata.items() if "Make" in k)
                    
                    mime = metadata.get('File:MIMEType', '')
                    
                    # Get Date from file modification
                    m_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    year_str = m_time.strftime("%Y")
                    month_str = m_time.strftime("%m-%B") # Updated to include name (e.g., 03-March)

                    # 1. Determine the Root Branch (Apple vs. Download)
                    if is_apple:
                        # Pure Apple Photos/Videos
                        target_folder = APPLE_PHOTOS_ROOT / year_str / month_str
                    else:
                        # Non-Apple (Screenshots, Downloads, etc.)
                        if "video" in mime:
                            category = "videos"
                        elif "png" in mime:
                            category = "images/screenshots"
                        else:
                            category = "images/saved"
                        
                        target_folder = DOWNLOADS_ROOT / category / year_str / month_str

                    # 2. Execute the Move
                    target_folder.mkdir(parents=True, exist_ok=True)
                    
                    dest_file = target_folder / file_path.name
                    if dest_file.exists():
                        ts = datetime.now().strftime("%H%M%S")
                        dest_file = target_folder / f"{file_path.stem}_{ts}{file_path.suffix}"

                    shutil.move(str(file_path), str(dest_file))
                    
                except Exception as e:
                    tqdm.write(f"⚠️ Error with {file_path.name}: {e}")
                
                pbar.update(1)

    print(f"\n✅ Done!")
    print(f"📸 Apple Originals: {APPLE_PHOTOS_ROOT}")
    print(f"📥 Downloads/Misc:  {DOWNLOADS_ROOT}")

if __name__ == "__main__":
    organize_media()
