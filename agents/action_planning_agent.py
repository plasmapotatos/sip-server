from utils.request_utils import process_and_prompt  # Import your processing function
from utils.prompts import ACTION_PLANNING_PROMPT

def plan_actions(filename):
    # Prompt for ChatGPT processing (example)
    prompt = ACTION_PLANNING_PROMPT

    # Process the video asynchronously
    response = process_and_prompt(filename, prompt, seconds_per_frame=1, use_all_frames=False)  # Adjust parameters as needed

    return response

if __name__ == "__main__":
    filename = 'saved_clips/clip_20240705-193514.mp4'  # Replace with your video path
    response = plan_actions(filename)
    print(response)