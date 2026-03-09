"""
Music Organizer
Author: Gerardo Galvan
Created: 2026-03-09
Description: A robust music library organizer that parses ID3/Metadata tags to 
             restructure files into 'Artist/Year - Album/XX Track.ext' format. 
             It also identifies images (covers/booklets) in song directories 
             and moves them into a dedicated 'artwork' subfolder.
Dependencies: tinytag, tqdm, rich
"""

import sys
import shutil
from pathlib import Path
from tinytag import TinyTag
from tqdm.rich import tqdm

def organize_music(source_dir):
    source_path = Path(source_dir).expanduser().resolve()
    target_path = source_path.parent / "Organized_Music"

    if not source_path.exists():
        print(f"❌ Error: The path {source_path} does not exist.")
        return

    # Define our file categories
    audio_exts = {'.mp3', '.flac', '.m4a', '.wav', '.ogg', '.mp4'}
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    
    # Get all files recursively
    all_files = list(source_path.rglob('*'))
    files = [f for f in all_files if f.suffix.lower() in (audio_exts | image_exts)]

    if not files:
        print(f"❓ No supported files found in {source_path}.")
        return

    print(f"🎵 Processing {len(files)} files...")

    for file in tqdm(files, desc="Organizing"):
        try:
            # --- CASE 1: AUDIO FILES ---
            if file.suffix.lower() in audio_exts:
                tag = TinyTag.get(file)
                
                artist = (tag.artist or "Unknown Artist").strip().replace("/", "-")
                album = (tag.album or "Unknown Album").strip().replace("/", "-")
                year = str(tag.year).split('-')[0] if tag.year else "0000"
                title = (tag.title or file.stem).strip().replace("/", "-")
                
                track_raw = str(tag.track).split('/')[0] if tag.track else "0"
                track_no = track_raw.zfill(2) if track_raw.isdigit() else "00"

                album_folder = f"{year} {album}"
                new_filename = f"{track_no} {title}{file.suffix}"
                
                dest_dir = target_path / artist / album_folder
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(file, dest_dir / new_filename)

            # --- CASE 2: IMAGE FILES ---
            elif file.suffix.lower() in image_exts:
                # To move images to the right place, we look at the folder they were in.
                # If the image is sitting next to a song, we put it in that song's new album folder.
                # We'll try to find metadata from a sibling music file to know where to put the art.
                sibling_audio = next((f for f in file.parent.glob('*') if f.suffix.lower() in audio_exts), None)
                
                if sibling_audio:
                    tag = TinyTag.get(sibling_audio)
                    artist = (tag.artist or "Unknown Artist").strip().replace("/", "-")
                    album = (tag.album or "Unknown Album").strip().replace("/", "-")
                    year = str(tag.year).split('-')[0] if tag.year else "0000"
                    
                    art_dir = target_path / artist / f"{year} {album}" / "artwork"
                else:
                    # If no audio file is nearby, put it in a general artwork bin
                    art_dir = target_path / "Unsorted_Artwork"

                art_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, art_dir / file.name)

        except Exception:
            continue

    print(f"\n✅ Done! Library organized at: {target_path}")

if __name__ == "__main__":
    folder_to_process = sys.argv[1] if len(sys.argv) > 1 else "."
    organize_music(folder_to_process)
