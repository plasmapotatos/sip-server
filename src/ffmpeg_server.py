import subprocess
import os
import time
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor  # Import ThreadPoolExecutor or ProcessPoolExecutor
from utils.request_utils import process_and_prompt  # Import your processing function
from utils.prompts import BASIC_PROMPT
from agents.fall_detection_agent import test_for_fall
from agents.action_planning_agent import plan_actions
from src.actions import speak, call, push_notification

# RTSP stream URL
RTSP_URL = "rtsp://169.233.172.175:8554/cam_with_audio"

# Directory to save clips
SAVE_DIR = "saved_clips"
os.makedirs(SAVE_DIR, exist_ok=True)
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
token = 'cA-0fbQARrO2ijGZ1UExle:APA91bEb0FCWo9QMu_eSuL7MhJSDsdsRJQiqlBifoQgRyouUnqxtPbYamiMpMy2_azJcWl3yg8LsfbusWWWJImwA6_F02-2dN1WufQXJ17oF3rz2kxsNr_4-v-GPfx_KFcelDe-XdbZs'

future = None

def pipeline(filename):
    # Test for a fall
    fall_detected = test_for_fall(filename)

    if fall_detected:
        # Plan actions
        response = plan_actions(filename)
    else:
        response = "No fall detected. No action needed."

    return response

# Function to capture and process video
def capture_and_process():
    while True:
        # Generate a unique filename with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(SAVE_DIR, f"clip_{timestamp}.mp4")

        # FFmpeg command to capture a 10-second chunk from the RTSP stream
        ffmpeg_command = [
            "ffmpeg",
            "-i", RTSP_URL,
            "-t", "10",
            "-c", "copy",
            filename
        ]

        # Execute FFmpeg command
        subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        print(f"Saved 10-second clip to {filename}")
        global future
        if future is not None:
            # Wait for the previous processing task to complete
            response = future.result()
            output_path = os.path.join(OUTPUT_DIR, f"gpt4o_output_{timestamp}.txt")
            with open(output_path, "w") as output_file:
                output_file.write(response)

            global token
            function_calls = re.findall(r'(\w+)\((.*?)\)', response)
            token = 'fFyqfZJWSUuNQS2cA1ec-A:APA91bGgD67k1KRb5pvrS5ViX28ufl_lRzz8BjKqYqbk7iHnmknyboM6kB0gZC_pRbtb1kvaNdG6zmX9phfJCloRqD4mIOuZwwyvTyms9KdO0naZky-6ebpJ4SuVgMkaaSzZwcTrjgmy'

            print(function_calls)
            for func_name, args in function_calls:
                new_args = f"{args}, '{token}'"  # Add the token to the arguments
                exec(f"{func_name}({new_args})")

        # Process the video asynchronously
        future = executor.submit(pipeline, filename)  # Adjust parameters as needed

        # Sleep for a short time to avoid overlapping chunks (optional)
        time.sleep(1)

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('fir-pushnotifications-17c1a-firebase-adminsdk-2gn9p-192b0078c5.json')
firebase_admin.initialize_app(cred)

# Set up ThreadPoolExecutor with desired number of threads
executor = ThreadPoolExecutor(max_workers=2)  # Adjust max_workers as needed

# Start capturing and processing videos
capture_and_process()
