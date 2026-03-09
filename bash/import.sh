#!/bin/bash

# Configuration
MOUNT_POINT="$HOME/iPhone"
DEST_DIR="$HOME/Pictures/temp/iPhone/Import_$(date +%Y-%m-%d)"

# 1. Create directories
mkdir -p "$MOUNT_POINT"
mkdir -p "$DEST_DIR"

# 2. Mount the device
echo "Attempting to mount iPhone..."
ifuse "$MOUNT_POINT" || { echo "Failed to mount. Is the iPhone unlocked and trusted?"; exit 1; }

# 3. Copy files (Flattening the random folder structure)
echo "Copying photos and videos to $DEST_DIR..."
find "$MOUNT_POINT/DCIM" -type f -exec cp --backup=numbered -v -t "$DEST_DIR" {} +

# 4. Optional: Convert HEIC to JPG (requires libheif-utils)
if command -v heif-convert &> /dev/null; then
    echo "Converting HEIC files to JPG..."
    cd "$DEST_DIR"
    for f in *.HEIC; do
        heif-convert "$f" "${f%.HEIC}.jpg" && rm "$f"
    done
else
    echo "Note: Install 'libheif-utils' from EPEL to auto-convert HEIC files."
fi

# 5. Cleanup
echo "Unmounting iPhone..."
cd ~
fusermount -u "$MOUNT_POINT"

echo "Done! Your photos are in $DEST_DIR"
