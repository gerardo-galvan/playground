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

    # Added .m4a and .alac for your Apple Lossless files
    audio_exts = {'.mp3', '.flac', '.m4a', '.alac', '.wav', '.ogg', '.mp4'}
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}

    all_files = [f for f in source_path.rglob('*') if f.is_file()]
    if not all_files:
        print(f"❓ No files found in {source_path}.")
        return

    # Pre-scan for artwork context
    folder_map = {}
    print("🔍 Pre-scanning for ALAC/Audio context...")
    for f in all_files:
        if f.suffix.lower() in audio_exts and f.parent not in folder_map:
            try:
                t = TinyTag.get(f)
                if t.artist and t.album:
                    folder_map[f.parent] = {
                        'artist': str(t.artist).strip().replace("/", "-"),
                        'album': str(t.album).strip().replace("/", "-"),
                        'year': str(t.year).split('-')[0] if t.year else "0000"
                    }
            except:
                continue

    print(f"🎵 Processing {len(all_files)} files...")

    for file in tqdm(all_files, desc="Moving files"):
        ext = file.suffix.lower()
        
        # --- AUDIO HANDLING ---
        if ext in audio_exts:
            try:
                tag = TinyTag.get(file)
                artist = (tag.artist or "Unknown Artist").strip().replace("/", "-")
                album = (tag.album or "Unknown Album").strip().replace("/", "-")
                year = str(tag.year).split('-')[0] if tag.year else "0000"
                title = (tag.title or file.stem).strip().replace("/", "-")
                track = str(tag.track).split('/')[0].zfill(2) if tag.track else "00"

                dest_dir = target_path / artist / f"{year} {album}"
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), str(dest_dir / f"{track} {title}{ext}"))
            except:
                shutil.move(str(file), str(target_path / "Unknown" / file.name))

        # --- IMAGE HANDLING ---
        elif ext in image_exts:
            # Check current folder or parent (if inside an 'artwork' folder)
            lookup_dir = file.parent if file.parent in folder_map else file.parent.parent
            
            if lookup_dir in folder_map:
                info = folder_map[lookup_dir]
                art_dest = target_path / info['artist'] / f"{info['year']} {info['album']}" / "artwork"
            else:
                art_dest = target_path / "_Unsorted_Artwork"

            art_dest.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(art_dest / file.name))

    # --- CLEANUP ---
    print("🧹 Cleaning up empty folders...")
    for empty_dir in sorted(source_path.rglob('*'), key=lambda x: len(str(x)), reverse=True):
        if empty_dir.is_dir() and not any(empty_dir.iterdir()):
            empty_dir.rmdir()

    print(f"\n✅ All set! Your library is ready at: {target_path}")

if __name__ == "__main__":
    folder_to_process = sys.argv[1] if len(sys.argv) > 1 else "."
    organize_music(folder_to_process)
