import av
import numpy as np
import torch
from transformers import VideoLlavaProcessor, VideoLlavaForConditionalGeneration

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

# print(run_video_llava("USER: <video>The person in the video either performs an Activity of Daily Life or falls in the video. Determine whether or not the person in the chronological series of images, which were extracted from a video, has fallen. Explain why you think the person has or has not fallen. ASSISTANT:", './data/Videos/video_(1).avi'))