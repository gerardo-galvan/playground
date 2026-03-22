import subprocess
import os
import platform
import argparse
from tqdm.rich import tqdm
from rich.console import Console

console = Console()

# Define your paths for both OS environments
# Logic: If Windows, use UNC paths. If Linux, use your mount points.
SYNC_CONFIG = {
    "movies": {
        "Windows": ("\\\\nas\\x\\Movies", "E:\\Movies"),
        "Linux": ("/mnt/nas/movies", "/mnt/usb/movies") 
    },
    "photos": {
        "Windows": ("\\\\nas\\Files\\Photos\\2026", "E:\\Photos\\2026"),
        "Linux": ("/mnt/nas/photos/2026", "/mnt/usb/photos/2026")
    }
}

def get_sync_command(src, dest):
    current_os = platform.system()
    
    if current_os == "Windows":
        # Robocopy flags: Mirror, Multi-threaded, Restartable mode
        return ["robocopy", src, dest, "/MIR", "/MT:8", "/R:5", "/W:5", "/NP"]
    
    else:
        # Rsync flags: Archive (recursive + perms), Verbose, Human-readable, Delete extras
        # --info=progress2 gives a single overall progress percentage
        return ["rsync", "-avh", "--delete", "--info=progress2", src, dest]

def run_universal_sync(category):
    current_os = platform.system()
    
    if category not in SYNC_CONFIG:
        console.print(f"[red]Category {category} not found in config.[/red]")
        return

    src, dest = SYNC_CONFIG[category][current_os]

    # Verify Destination (BitLocker drive on Win / Mount point on Linux)
    if not os.path.exists(dest if current_os == "Windows" else os.path.dirname(dest)):
        console.print(f"[bold red]Error:[/bold red] Destination {dest} not reachable!")
        return

    cmd = get_sync_command(src, dest)
    
    console.print(f"[bold cyan]OS Detected:[/bold cyan] {current_os}")
    console.print(f"[bold green]Running:[/bold green] {' '.join(cmd)}")

    try:
        # Using subprocess.run for simplicity; rsync/robocopy 
        # will print their own progress to the terminal.
        subprocess.run(cmd, check=False) 
    except Exception as e:
        console.print(f"[red]Failed to execute sync: {e}[/red]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--movies", action="store_true")
    parser.add_argument("-p", "--photos", action="store_true")
    args = parser.parse_args()

    if args.movies: run_universal_sync("movies")
    elif args.photos: run_universal_sync("photos")
    else: parser.print_help()