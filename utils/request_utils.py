import cv2
from moviepy.editor import VideoFileClip
import base64
import numpy as np
from openai import OpenAI 

import os
import openai
import requests
from utils.prompts import ACTION_PLANNING_PROMPT, SAFETY_SCORE_PROMPT

# Set your OpenAI API key
MODEL = "gpt-4o"
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_transcription(audio_path):
    # Get the transcription of the audio
    if audio_path is not None:
        try:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=open(audio_path, "rb"),
            ).text
        except Exception as e:
            print(f"Error: {e}")
            transcription = ""
    else:
        transcription = ""
        
    return transcription

def process_video(video_path, seconds_per_frame=2, use_all_frames=False):
    base64Frames = []
    base_video_path, _ = os.path.splitext(video_path)

    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
    frames_to_skip = int(fps * seconds_per_frame)
    curr_frame = 0

    if use_all_frames:
        frames_to_skip = 1

    # Loop through the video and extract frames at specified sampling rate
    print(total_frames)
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
    try: 
        audio_path = f"{base_video_path}.mp3"
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_path, bitrate="32k")
        clip.audio.close()
        clip.close()
    except Exception as e:
        print(f"Error: {e}")
        audio_path = None

    #print(f"Extracted {len(base64Frames)} frames")
    #print(f"Extracted audio to {audio_path}")
    return base64Frames, audio_path

def prompt_gpt4o_with_frames_and_audio(base64Frames, user_prompt, transcription):
    # Send the combined prompt to GPT-4O
    while True:
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                {"role": "system", "content": user_prompt},
                {"role": "user", "content": [
                    "These are the frames from the video.",
                    *map(lambda x: {"type": "image_url", 
                                    "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames),
                    {"type": "text", "text": f"The audio transcription is: {transcription}"}
                    ],
                }
                ],
                temperature=0,
            )
            output = response.choices[0].message.content
            break
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    return output

def prompt_gpt4o(user_prompt):
    # Send the user prompt to GPT-4O
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
        {"role": "user", "content": user_prompt
        }
        ],
        temperature=0,
    )

    return response.choices[0].message.content

def prompt_gpt4o_with_image(user_prompt, image):
    #image in cv2 format
    _, buffer = cv2.imencode(".jpg", image)
    base64Image = base64.b64encode(buffer).decode("utf-8")

    # Send the user prompt and image to GPT-4O
    response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "user", "content": [
            {"type": "text", "text": user_prompt},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{base64Image}"}
            }
        ]}
    ],
    temperature=0.0,
)

    return response.choices[0].message.content

def process_and_prompt(video_path, prompt, seconds_per_frame=2, use_all_frames=False):
    # Process the video to get frames and audio
    base64Frames, audio_path = process_video(video_path, seconds_per_frame, use_all_frames=use_all_frames)

    if audio_path is not None:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=open(audio_path, "rb"),
        ).text
    else:
        transcription = ""

    print(f"Transcription: {transcription}")

    # Get the response from GPT-4O using the base64 frames and the user prompt
    response = None
    if base64Frames:
        response = prompt_gpt4o_with_frames_and_audio(base64Frames, prompt, transcription)

    return response

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def prompt_sam(image_str):
    # URL of the endpoint
    url = 'http://127.0.0.1:5000/api/inference'
    # Send the image and prompt to the SAM endpoint
    data = {
        'image': image_str,
        'annotation_mode': ['Mark', 'Polygon'],
        'mask_alpha': 0.05
    }

    try:
        response = requests.post(url, json=data)
        response_data = response.json()

        try:
            response_data = response.json()
        except ValueError:
            print(f"Error: Response is not in JSON format. Response text: {response.text}")
            return None
        
        if 'result_image' not in response_data:
            print("Error: 'result_image' key not found in the response.")
            return None

        result_image_str = response_data['result_image']
        result_image_data = base64.b64decode(result_image_str)
        
        # Convert base64 to image
        nparr = np.frombuffer(result_image_data, np.uint8)
        result_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        return result_image

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


if __name__ == "__main__":
    image_path = 'room.png'
    image_str = encode_image(image_path)
    image = prompt_sam(image_str)

    cv2.imwrite('result_image_from_video.jpg', image)

    response = prompt_gpt4o_with_image(SAFETY_SCORE_PROMPT, image)

    print(response)
