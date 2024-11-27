#!/bin/bash

# Check if the user provided a file path
if [ $# -eq 0 ]; then
    echo "Usage: $0 <PATH_TO_FILE>"
    exit 1
fi

# Get the absolute path of the file
FILE_PATH=$(realpath "$1")

# Verify that the file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File '$FILE_PATH' does not exist."
    exit 1
fi

# Run the Docker container, mounting the file and passing it to the program
docker run --rm -it -v "$FILE_PATH:/app/input.bs" script_debugger python /app/python/src/dbg.py -file /app/input.bs

