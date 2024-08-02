import io
import av
import numpy as np
import cv2
import base64

import gradio as gr
import torch
from PIL import Image
from transformers import VideoLlavaProcessor, VideoLlavaForConditionalGeneration
from utils.safety_scores import get_safety_score_info

# Load the pre-trained model and tokenizer
device = "cuda:0"

model = VideoLlavaForConditionalGeneration.from_pretrained("LanguageBind/Video-LLaVA-7B-hf").to(device)
processor = VideoLlavaProcessor.from_pretrained("LanguageBind/Video-LLaVA-7B-hf")

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

# Define the inference function
def prompt_videollava(prompt, video_path):        # added img_path
    # Preprocess the image
    print(video_path)
    container = av.open(video_path)

    # sample uniformly 8 frames from the video
    total_frames = container.streams.video[0].frames
    indices = np.arange(0, total_frames, container.streams.video[0].average_rate).astype(int)
    clip = read_video_pyav(container, indices)

    result_image, safety_score_info = get_safety_score_info(video_path)
    cv2.imwrite('result_image_from_video.jpg', result_image)

    _, buffer = cv2.imencode(".jpg", result_image)
    base64Image = base64.b64encode(buffer).decode("utf-8")

    img_data = base64.b64decode(base64Image)
    img = Image.open(io.BytesIO(img_data)).convert("RGB")
    img = np.array(img)
    img = np.expand_dims(img, axis=0)  # Add batch dimension

    # Combine the video frames and the additional image
    combined_clip = np.concatenate((img, clip), axis=0)

    inputs = processor(text=prompt, videos=combined_clip, return_tensors="pt").to(device)

    # Generate
    generate_ids = model.generate(**inputs, max_length=1000)
    return processor.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]


# Create the Gradio interface
iface = gr.Interface(
    fn=prompt_videollava,
    inputs=[
        gr.Textbox(label="Prompt"),
        gr.Video(label="Upload Video"),
    ],
    outputs="text",
    title="VideoLLaVA test",
    description="Enter a prompt and upload a video.",
)

# Launch the Gradio app
iface.launch()