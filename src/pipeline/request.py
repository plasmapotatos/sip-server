from openai import OpenAI 
from loader import load_vids
import os
import cv2
from moviepy.editor import VideoFileClip
import time
import requests
import base64
import av
import json
from gradio_client import Client, handle_file
import numpy as np
from transformers import VideoLlavaProcessor, VideoLlavaForConditionalGeneration
from videollava import run_video_llava

class BaselineModel:
    def __init__(self, model_name, seconds_per_frame=1):
        self.model_name = model_name
        self.MODEL = "gpt-4o"
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Extract 1 frame per second. You can adjust the `seconds_per_frame` parameter to change the sampling rate
        self.seconds_per_frame = seconds_per_frame
    
    #converts video into a list of images (base64Frames) and returns an audio_path
    def process_video(self, video_path):
        #taken from GPT-4o website
        base64Frames = []
        base_video_path, _ = os.path.splitext(video_path)

        video = cv2.VideoCapture(video_path)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        fps = video.get(cv2.CAP_PROP_FPS)
        frames_to_skip = int(fps * self.seconds_per_frame)
        curr_frame=0

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
        # clip = VideoFileClip(video_path)
        # clip.audio.write_audiofile(audio_path, bitrate="32k")
        # clip.audio.close()
        # clip.close()

        # print(f"Extracted {len(base64Frames)} frames")
        # print(f"Extracted audio to {audio_path}")
        print(video_path + " done.")
        return base64Frames, audio_path
    
    #takes the list of images and feeds it into GPT-4o to get either yes or no
    def get_response(self, vid_path):
        base64Frames, audio_path = BaselineModel.process_video(self, video_path=vid_path)
        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
            {"role": "system", "content": "You are determining whether or not the person in the chronological series of images, which were extracted from a video, has fallen. Begin your response with just one capital letter: either Y or N. Finish your response with an explanation of why you believe that the person has fallen."},
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
    
    #iterates through all videos and returns a list containing all their predictions
    def predict(self, directory):
        video_paths = load_vids(directory)
        predictions = []

        for video_path in video_paths:
            output = self.get_response(vid_path=video_path)
            predictions.append(output)

        return predictions
    
    def predict_custom(self, directory, vidnums):
        video_paths = load_vids(directory)
        predictions = []

        for n in vidnums:
            output = self.get_response(vid_path=video_paths[n - 1])
            predictions.append(output)

        return predictions

class VideoLLaVA:
    def __init__(self, model_name):
        self.model_name = model_name

    def get_response(self, video_path, client=None):
        if not client:
            print("need to make client :(")
            client = Client("http://127.0.0.1:7860")
        prompt = "USER: <video>Does the person fall in this video? Begin your response with either the word YES or NO. ASSISTANT:"
        try:
            output = client.predict(
                prompt=prompt,
                video_path={"video":handle_file(video_path)},
                api_name="/predict",
            )
            return output
        except requests.exceptions.RequestException as e:
            print("Error:", e)
    
    def predict(self, directory):
        video_paths = load_vids(directory)
        predictions = []

        for video_path in video_paths:
            output = self.get_response(video_path=video_path)
            predictions.append(output)

        return predictions
    
    def predict_custom(self, directory, vidnums, client=None):
        video_paths = load_vids(directory)
        predictions = []

        for n in vidnums:
            output = self.get_response(video_path=video_paths[n], client=client)
            predictions.append(output)

        return predictions
        

if __name__ == '__main__':
    predictions = VideoLLaVA('Video-LLaVA').predict_custom(directory='.', vidnums=[0])
    for i in predictions:
        print(i)