import base64
import copy
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from urllib.parse import parse_qs, urlparse

import requests
import torch
from PIL import Image

import av
import numpy as np
import torch
from transformers import VideoLlavaProcessor, VideoLlavaForConditionalGeneration

model = VideoLlavaForConditionalGeneration.from_pretrained("LanguageBind/Video-LLaVA-7B-hf")
processor = VideoLlavaProcessor.from_pretrained("LanguageBind/Video-LLaVA-7B-hf")


# Define the HTTP request handler
class RequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    # Define the do_GET method to handle GET requests
    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        post_data = self.rfile.read(content_length).decode("utf-8")

        parsed_data = parse_qs(post_data)
        print(len(parsed_data["videos"]))

        if "prompt" in parsed_data:
            video_paths = None
            videos = None
            if "video_paths" in parsed_data:
                video_paths = parsed_data["video_paths"][0]
            elif "videos" in parsed_data:
                image_b64s = parsed_data["videos"]
                image_bytes = [base64.b64decode(image_b64) for image_b64 in image_b64s]
                videos = [Image.open(BytesIO(image_byte)) for image_byte in image_bytes]
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing image")
                return
            prompt = parsed_data["prompt"][0]

            print(prompt, videos)

            result = prompt_videollava(prompt, video_paths, videos)
            self._set_response()
            self.wfile.write(str(result).encode())
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Missing parameters")


def read_video_pyav(container, indices):
    frames = []
    container.seek(0)
    start_index = indices[0]
    end_index = indices[-1]
    for i, frame in enumerate(container.decode(video=0)):
        if i > end_index:
            break
        if i >= start_index and i in indices:
            frames.append(frame)
    return np.stack([x.to_ndarray(format="rgb24") for x in frames])

def prompt_videollava(prompt, video_paths=None, videos=None):
    print("prompt:", prompt)
    if video_paths is None and videos is None:
        raise ValueError("Either image_path or image must be provided.")
    if video_paths is not None:
        videos = []
        for image_path in video_paths:
            image = Image.open(image_path)
            videos.append(image)

    results = []

    for video_path in video_paths:
        container = av.open(video_path)

        # sample uniformly 8 frames from the video
        total_frames = container.streams.video[0].frames
        indices = np.arange(0, total_frames, total_frames / 8).astype(int)
        clip = read_video_pyav(container, indices)

        inputs = processor(text=prompt, videos=clip, return_tensors="pt")

        # Generate
        generate_ids = model.generate(**inputs, max_length=80)

        output = processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

        results.append(output)
    print(results)

    return results


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
