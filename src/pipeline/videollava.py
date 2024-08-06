import av
import numpy as np
import torch
import cv2
import base64
import io
from PIL import Image
from transformers import VideoLlavaProcessor, VideoLlavaForConditionalGeneration
from utils.safety_scores import get_safety_score_info
from utils.prompts import FALL_DETECTION_PROMPT_WITH_SAFETY_SCORE_VLLAVA

device = "cuda:0"

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

def run_video_llava(prompt, video_path):
    model = VideoLlavaForConditionalGeneration.from_pretrained("LanguageBind/Video-LLaVA-7B-hf")
    processor = VideoLlavaProcessor.from_pretrained("LanguageBind/Video-LLaVA-7B-hf")

    container = av.open(video_path)

    # sample uniformly 8 frames from the video
    total_frames = container.streams.video[0].frames
    indices = np.arange(0, total_frames, total_frames / 8).astype(int)
    clip = read_video_pyav(container, indices)

    inputs = processor(text=prompt, videos=clip, return_tensors="pt")

    # Generate
    generate_ids = model.generate(**inputs, max_length=300)
    return processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

def run_video_llava_with_sam(prompt, video_path, result_image):
    model = VideoLlavaForConditionalGeneration.from_pretrained("LanguageBind/Video-LLaVA-7B-hf", device_map="auto")
    processor = VideoLlavaProcessor.from_pretrained("LanguageBind/Video-LLaVA-7B-hf")

    container = av.open(video_path)

    # Sample uniformly 8 frames from the video
    total_frames = container.streams.video[0].frames
    indices = np.arange(0, total_frames, container.streams.video[0].average_rate).astype(int)
    clip = read_video_pyav(container, indices)

    # Resize result_image to match the frame size
    frame_height, frame_width, _ = clip[0].shape
    result_image = cv2.resize(result_image, (frame_width, frame_height))

    # Convert result_image to numpy array in the required format
    result_image = np.array(result_image)
    result_image = np.expand_dims(result_image, axis=0)  # Add batch dimension

    # Combine the video frames and the additional image
    combined_clip = np.concatenate((result_image, clip), axis=0)

    inputs = processor(text=prompt, videos=combined_clip, return_tensors="pt")

    # Generate
    generate_ids = model.generate(**inputs, max_length=3000)
    return processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

result_image, safety_score_info = get_safety_score_info('./data/Videos/video_(47).avi')
prompt = "USER: <video>" + FALL_DETECTION_PROMPT_WITH_SAFETY_SCORE_VLLAVA.format(safety_score_info=safety_score_info) + " ASSISTANT:"
print(run_video_llava_with_sam(prompt, './data/Videos/video_(47).avi', result_image))
