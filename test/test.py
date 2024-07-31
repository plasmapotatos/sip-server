import re
import cv2
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from src.actions import speak, call, push_notification
from src.ffmpeg_server import chat_with_client, build_conversation
from utils.prompts import CONVERSATION_PROMPT
from utils.video_utils import get_video_frames, encode_image_to_base64
from utils.request_utils import prompt_sam

if __name__ == "__main__":
    # Load the video frames
    video_path = "resized_video.avi"
    frames = get_video_frames(video_path)

    image = frames[0]

    # Encode the image to base64
    image_str = encode_image_to_base64(image)

    # Prompt SAM with the image
    result_image = prompt_sam(image_str)

    # Save the result image
    cv2.imwrite('result_image_from_video.jpg', result_image)
