#!/bin/bash

# RTSP stream URL
RTSP_URL="rtsp://192.168.1.25:8554/cam_with_audio"

# Directory to save clips
SAVE_DIR="saved_clips"
mkdir -p "$SAVE_DIR"

while true; do
    # Generate a unique filename with a timestamp
    TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
    FILENAME="$SAVE_DIR/clip_$TIMESTAMP.mp4"

    # Use FFmpeg to capture a 10-second chunk from the RTSP stream
    ffmpeg -i "$RTSP_URL" -t 10 -c copy "$FILENAME"

    echo "Saved 10-second clip to $FILENAME"

    # Sleep for a short time to avoid overlapping chunks (optional)
    sleep 1
done
