import subprocess
import os
import sys
import argparse
from datetime import datetime

# Configuration Dictionary
SYNC_PATHS = {
    "movies": ("\\\\nas\\x\\Movies", "E:\\Movies"),
    "tv": ("\\\\nas\\x\\TV Shows", "E:\\TV Shows"),
    "music": ("\\\\nas\\x\\Music", "E:\\Music"),
    "books": ("\\\\nas\\x\\Books", "E:\\Books"),
    "downloads": ("\\\\nas\\x\\Downloads", "E:\\Downloads"),
    "photos": ("\\\\nas\\Files\\Photos\\Albums\\Imports\\iPhone\\", "E:\\Files\\Photos\\Albums\\Imports\\iPhone\\"),
  "temp": ("\\\\nas\\x\\Temp", "E:\\Temp"),
}

def run_backup(category):
    if category not in SYNC_PATHS:
        print(f"Unknown category: {category}")
        return

    src, dest = SYNC_PATHS[category]
    log_file = f"C:\\temp\\nas_sync_{category}.txt"
    
    # 1. Ensure Log Directory Exists
    os.makedirs("C:\\temp", exist_ok=True)

    # 2. Check if BitLocker Drive (E:) is mounted
    if not os.path.exists("E:\\"):
        print(f"Error: Drive E: not found. Is your BitLocker drive unlocked?")
        sys.exit(1)

    # 3. Build Robocopy Command
    # /TEE: output to console AND log, /NP: No Progress (cleaner logs)
    cmd = [
        "robocopy", src, dest,
        "/MIR", "/MT:8", "/R:5", "/W:5", "/NP", "/TEE",
        f"/LOG:{log_file}"
    ]

    print(f"--- Starting {category.capitalize()} Sync ---")
    print(f"Source: {src} -> Dest: {dest}")
    
    # 4. Execute
    try:
        # Robocopy uses non-zero exit codes for success (1-7), so we don't check_returncode
        subprocess.run(cmd)
        print(f"Done! Log saved to {log_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NAS to External HD Backup Script")
    # Add flags for each category
    parser.add_argument("-m", "--movies", action="store_true")
    parser.add_argument("-t", "--tv", action="store_true")
    parser.add_argument("-mu", "--music", action="store_true")
    parser.add_argument("-b", "--books", action="store_true")
    parser.add_argument("-d", "--downloads", action="store_true")
    parser.add_argument("-p", "--photos", action="store_true")
    parser.add_argument("-temp", "--temp", action="store_true")


    args = parser.parse_args()

    # Map the flags to the function
    mapping = {
        "movies": args.movies,
        "tv": args.tv,
        "music": args.music,
        "books": args.books,
        "downloads": args.downloads,
        "photos": args.photos,
	"temp": args.temp
    }

    # Run the backup for whichever flag was triggered
    selected = [k for k, v in mapping.items() if v]
    if selected:
        for cat in selected:
            run_backup(cat)
    else:
        parser.print_help()