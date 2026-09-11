#!/bin/bash

# Check if the user provided a file path
if [ $# -eq 0 ]; then
    echo "Usage: $0 <PATH_TO_FILE>"
    exit 1
fi

# Verify that the file exists before resolving it. realpath on a missing path
# writes its own error and returns nothing, which used to leave the message
# below reporting an empty filename.
if [ ! -f "$1" ]; then
    echo "Error: File '$1' does not exist."
    exit 1
fi

# Get the absolute path of the file
FILE_PATH=$(realpath "$1")

# Run the Docker container, mounting the file and passing it to the program
docker run --rm -it -v "$FILE_PATH:/app/input.bs" script_debugger python3 /app/python/src/dbg.py -file /app/input.bs
