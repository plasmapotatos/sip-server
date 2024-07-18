from utils.request_utils import process_and_prompt  # Import your processing function
from utils.prompts import FALL_DETECTION_PROMPT

def process_response(response):
    # Process the response to extract the model's output
    output = response.split("<output>")[1].split("</output>")[0]

    return output

def test_for_fall(filename):
    # Prompt for ChatGPT processing (example)
    prompt = FALL_DETECTION_PROMPT

    # Process the video asynchronously
    response = process_and_prompt(filename, prompt, seconds_per_frame=1, use_all_frames=False)  # Adjust parameters as needed

    # Process the response
    if response:
        processed_response = process_response(response)
    else:
        processed_response = "no"

    if processed_response == "yes":
        output = True
    else:
        output = False
    return output, response

if __name__ == "__main__":
    filename = 'saved_clips/clip_20240705-193514.mp4'  # Replace with your video path
    response = test_for_fall(filename)
    print(response)