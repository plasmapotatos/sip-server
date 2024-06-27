import cv2
from moviepy.editor import VideoFileClip
import base64
from openai import OpenAI 

import os
import openai
from utils.prompts import BASIC_PROMPT

# Set your OpenAI API key
MODEL = "gpt-4o"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def process_video(video_path, seconds_per_frame=2):
    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)

    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame = 0

    # Loop through the video and extract frames at specified sampling rate
    while curr_frame < total_frames - 1:
        video.set(cv2.CAP_PROP_POS_FRAMES, curr_frame)
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        curr_frame += frames_to_skip
    video.release()

    # Extract audio from video
    audio_path = f"{base_video_path}.mp3"
    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_path, bitrate="32k")
    clip.audio.close()
    clip.close()

    print(f"Extracted {len(base64Frames)} frames")
    print(f"Extracted audio to {audio_path}")
    return base64Frames, audio_path

def prompt_gpt4o_with_frames(base64Frames, user_prompt):
    # Send the combined prompt to GPT-4O
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
        {"role": "system", "content": user_prompt},
        {"role": "user", "content": [
            "These are the frames from the video.",
            *map(lambda x: {"type": "image_url", 
                            "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames)
            ],
        }
        ],
        temperature=0,
    )
    
    return response.choices[0].message.content

def process_and_prompt(video_path, prompt, seconds_per_frame=2):
    # Process the video to get frames and audio
    base64Frames, audio_path = process_video(video_path, seconds_per_frame)

    # Get the response from GPT-4O using the base64 frames and the user prompt
    response = prompt_gpt4o_with_frames(base64Frames, prompt)

    return response

# Example usage
video_path = 'video_1.avi'  # Replace with your video path
user_prompt = BASIC_PROMPT

response = process_and_prompt(video_path, user_prompt, seconds_per_frame=1)
print(response)
