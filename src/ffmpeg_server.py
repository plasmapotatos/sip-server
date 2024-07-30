import subprocess
import os
import time
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed  # Import ThreadPoolExecutor and as_completed
from utils.request_utils import process_and_prompt, prompt_gpt4o  # Import your processing function
from utils.prompts import BASIC_PROMPT, CONVERSATION_PROMPT
from agents.fall_detection_agent import test_for_fall
from agents.action_planning_agent import plan_actions
from src.actions import speak, call, push_notification, listen_for_feedback

# RTSP stream URL
RTSP_URL = "rtsp://169.233.172.175:8554/cam_with_audio"

# Directory to save clips
SAVE_DIR = "saved_clips"
os.makedirs(SAVE_DIR, exist_ok=True)
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# Initialize the Firebase Admin SDK
cred = credentials.Certificate('fir-pushnotifications-17c1a-firebase-adminsdk-2gn9p-192b0078c5.json')
firebase_admin.initialize_app(cred)

token = 'fFyqfZJWSUuNQS2cA1ec-A:APA91bGGQ-_r9xHje45dILAWkhRyiFOLyQvQslwy5zmE36yli0whteKozOpOQ81LMGo2ukmdwW534JViuf6P8SN0wkRumCcAQOd2Ephhj_CIU_yEUhRoe-QyyNEl34IQBdxc5UBOj3pd'

def pipeline(filename):
    # Test for a fall
    fall_detected, output = test_for_fall(filename)

    if fall_detected:
        # Plan actions
        print("Fall detected. Planning actions...")
        response = plan_actions(filename)
    else:
        print(f"No fall detected. No action needed. Reasoning: {output}")
        response = "No fall detected. No action needed. Reasoning: " + output

    return response

def build_conversation(agent, client):
    conversation = ""
    for i in range(len(agent)):
        conversation += f"Agent: {agent[i]}\nClient: {client[i]}\n"
    return conversation

def process_result(question, result):
    return result[len(question):]

def estimate_tts_duration(text, words_per_minute=170):
    words = len(text.split())
    duration_minutes = words / words_per_minute
    duration_seconds = duration_minutes * 60
    return duration_seconds    

def chat_with_client(agent, client, previous):
    done = False
    while not done:
        conversation = build_conversation(agent, client)
        prompt = CONVERSATION_PROMPT.format(conversation=conversation)
        print("Conversation:", conversation)
        response = prompt_gpt4o(prompt)
        print("Response:", response)
        
        function_calls = re.findall(r'(\w+)\((.*?)\)', response)
        print("Function calls:", function_calls)
        done = True
        previous_question = previous
        for func_name, args in function_calls:
            if func_name != 'listen_for_feedback':
                new_args = f"{args}, '{token}'"  # Add the token to the arguments
            else:
                estimated_duration = estimate_tts_duration(previous_question)
                new_args = f"'{estimated_duration}'"
            exec(f"""global result
result = {func_name}({new_args})""")
            if func_name == 'speak':
                previous_question = args[:-3]
                agent.append(args[:-3])
            if func_name == 'listen_for_feedback':
                #print("previous_question:", previous_question)
                #print("result:", result)
                processed_result = process_result(previous_question, result)
                #print("processed_result:", processed_result)
                client.append(result)
                done = False

# Function to capture and process video
def capture_video():
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

        yield filename

        time.sleep(8)

# Function to process each video chunk
def process_video_chunk(filename):
    response = pipeline(filename)
    timestamp = filename.split('_')[-1].split('.')[0]
    output_path = os.path.join(OUTPUT_DIR, f"gpt4o_output_{timestamp}.txt")
    with open(output_path, "w") as output_file:
        output_file.write(response)

    function_calls = re.findall(r'(\w+)\((.*?)\)', response)

    agent = []
    client = []
    for func_name, args in function_calls:
        if func_name != 'listen_for_feedback':
            new_args = f"{args}, '{token}'"  # Add the token to the arguments
        else:
            estimated_duration = estimate_tts_duration(previous_question)
            new_args = f"'{estimated_duration}'"
        exec(f"""global result
result = {func_name}({new_args})""")
        if func_name == 'speak':
            previous_question = args[:-3]
            agent.append(args[:-3])
        if func_name == 'listen_for_feedback':
            #print("previous_question:", previous_question)
            #print("result:", result)
            processed_result = process_result(previous_question, result)
            #print("processed_result:", processed_result)
            client.append(result)
            chat_with_client(agent, client, previous_question)

if __name__ == "__main__":
    # # Initialize the Firebase Admin SDK
    # cred = credentials.Certificate('fir-pushnotifications-17c1a-firebase-adminsdk-2gn9p-192b0078c5.json')
    # firebase_admin.initialize_app(cred)

    fall_video_path = "falls/clip_20240717-114123.mp4"
    #process_video_chunk(fall_video_path)

    # Set up ThreadPoolExecutor with desired number of threads
    executor = ThreadPoolExecutor(max_workers=4)  # Adjust max_workers as needed

    # Start capturing and processing videos
    video_generator = capture_video()
    futures = {executor.submit(process_video_chunk, filename): filename for filename in video_generator}

    try:
        for future in as_completed(futures):
            filename = futures[future]
            try:
                result = future.result()
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    finally:
        executor.shutdown()
