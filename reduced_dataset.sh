#!/bin/bash

# Check if correct number of arguments provided
if [ $# -ne 4 ]; then
    echo "Usage: $0 <source_dir> <target_dir> <percentage> <file_extension>"
    echo "Example: $0 /path/to/source /path/to/target 25 jpg"
    echo "Example: $0 /path/to/source /path/to/target 50 png"
    echo "Example: $0 /path/to/source /path/to/target 10 '*' (for all files)"
    exit 1
fi

source_dir="$1"
target_dir="$2"
percentage="$3"
file_extension="$4"

# Validate percentage is a number between 1 and 100
if ! [[ "$percentage" =~ ^[0-9]+$ ]] || [ "$percentage" -lt 1 ] || [ "$percentage" -gt 100 ]; then
    echo "Error: Percentage must be a number between 1 and 100"
    exit 1
fi

# Check if source directory exists
if [ ! -d "$source_dir" ]; then
    echo "Error: Source directory '$source_dir' does not exist"
    exit 1
fi

# Create target directory if it doesn't exist
if [ ! -d "$target_dir" ]; then
    echo "Creating target directory: $target_dir"
    mkdir -p "$target_dir"
fi

# Count total files of specified type
total_files=$(find "$source_dir" -maxdepth 1 -type f -iname "*.$file_extension" | wc -l)

if [ "$total_files" -eq 0 ]; then
    echo "No *.$file_extension files found in source directory"
    exit 1
fi

# Calculate number of files to copy (round up)
num_files=$(( (total_files * percentage + 99) / 100 ))

echo "Found $total_files *.$file_extension files. Copying first $num_files files ($percentage%) from '$source_dir' to '$target_dir'..."

# Copy the calculated number of files with numerical sorting
find "$source_dir" -maxdepth 1 -type f -iname "*.$file_extension" | sort -V | head -"$num_files" | xargs -I {} cp {} "$target_dir/"

echo "Done! Copied $num_files out of $total_files *.$file_extension files."
