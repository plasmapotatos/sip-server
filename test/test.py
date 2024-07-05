import subprocess
import os
import time

# RTSP stream URL
rtsp_url = 'rtsp://192.168.1.25:8554/cam_with_audio'

# Directory to save clips
save_path = 'saved_clips'
if not os.path.exists(save_path):
    os.makedirs(save_path)

ffmpeg_process = None

def start_recording():
    global ffmpeg_process
    if ffmpeg_process is None:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        clip_name = f'clip_{timestamp}.mp4'
        clip_path = os.path.join(save_path, clip_name)

        ffmpeg_command = [
            'ffmpeg',
            '-i', rtsp_url,
            '-c', 'copy',
            clip_path
        ]

        # Redirect stdout and stderr to subprocess.DEVNULL to silence FFmpeg output
        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Recording started. Saving to {clip_path}. Type 'stop' to stop recording.")

def stop_recording():
    global ffmpeg_process
    if ffmpeg_process is not None:
        ffmpeg_process.terminate()
        ffmpeg_process = None
        print("Recording stopped. Type 'start' to start recording again.")

while True:
    command = input("Type 'start' to start recording, 'stop' to stop recording, and 'quit' to exit: ").strip().lower()
    if command == 'start':
        start_recording()
    elif command == 'stop':
        stop_recording()
    elif command == 'quit':
        stop_recording()
        break
    else:
        print("Invalid command. Please type 'start', 'stop', or 'quit'.")

print("Program terminated.")
