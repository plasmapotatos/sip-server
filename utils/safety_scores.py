import cv2
from utils.prompts import SAFETY_SCORE_PROMPT
from utils.video_utils import get_video_frames, encode_image_to_base64
from utils.request_utils import prompt_sam, prompt_gpt4o_with_image

def get_safety_score_info(video_path):
    frames = get_video_frames(video_path)

    image = frames[0]

    # Encode the image to base64
    image_str = encode_image_to_base64(image)

    # Prompt SAM with the image
    result_image = prompt_sam(image_str)
    cv2.imwrite('result_image_from_video.jpg', result_image)

    response = prompt_gpt4o_with_image(SAFETY_SCORE_PROMPT, result_image)

    return result_image, response

if __name__ == "__main__":
    video_path = "resized_video.avi"
    result_image, safety_score_info = get_safety_score_info(video_path)
    print(safety_score_info)
