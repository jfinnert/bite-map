#!/bin/bash

# This script migrates unique tests from app/tests to tests/
# It compares files and only copies over tests that are different or don't exist in the root tests directory

# Make the script executable
chmod +x "$0"

# Set the source and target directories
SRC_DIR="app/tests"
TARGET_DIR="tests"

# Check if test directories exist
if [ ! -d "$SRC_DIR" ]; then
    echo "Source directory $SRC_DIR doesn't exist!"
    exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
    echo "Target directory $TARGET_DIR doesn't exist!"
    exit 1
fi

# Find all Python files in the source directory
find "$SRC_DIR" -type f -name "*.py" | while read -r src_file; do
    # Get the relative path from the source dir
    rel_path="${src_file#$SRC_DIR/}"
    # Construct the target file path
    target_file="$TARGET_DIR/$rel_path"
    target_dir="$(dirname "$target_file")"
    
    # Create target directory if it doesn't exist
    if [ ! -d "$target_dir" ]; then
        mkdir -p "$target_dir"
        echo "Created directory: $target_dir"
    fi
    
    # Check if the file exists in the target dir
    if [ -f "$target_file" ]; then
        # If the file exists, check if it's different
        if ! diff -q "$src_file" "$target_file" > /dev/null; then
            echo "File $rel_path differs between directories"
            echo "Backing up original file"
            cp "$target_file" "${target_file}.bak"
            echo "Copying $src_file to $target_file"
            cp "$src_file" "$target_file"
            echo "Updated: $target_file (backup saved as ${target_file}.bak)"
        else
            echo "File $rel_path is identical in both directories - skipping"
        fi
    else
        # If the file doesn't exist in the target, copy it
        echo "Copying $src_file to $target_file (new file)"
        cp "$src_file" "$target_file"
    fi
done

echo ""
echo "Migration complete!"
echo "--------------------------------------------------------------------------------"
echo "Please check the files in $TARGET_DIR and resolve any import path issues."
echo "After verifying that all tests run correctly, you can remove $SRC_DIR."
echo "Run the tests with: make test-in-container"
