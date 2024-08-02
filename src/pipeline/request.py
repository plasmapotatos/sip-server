from openai import OpenAI 
from loader import load_vids
import os
import cv2
import requests
import base64
from gradio_client import Client, handle_file
from utils.safety_scores import get_safety_score_info
from utils.prompts import FALL_DETECTION_PROMPT_WITH_SAFETY_SCORE

class BaselineModel:
    def __init__(self, model_name='gpt-4o-mini', seconds_per_frame=1):
        self.model_name = model_name
        self.MODEL = 'gpt-4o-mini'
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
    
    def process_certain_frames(self, video_path, frames):
        #taken from GPT-4o website
        base64Frames = []
        base_video_path, _ = os.path.splitext(video_path)

        video = cv2.VideoCapture(video_path)
        
        for n in frames:
            video.set(cv2.CAP_PROP_POS_FRAMES, n)
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
        video.release()

        return base64Frames
    
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
    
    def get_safety_score_response(self, vid_path, segmented_image, safety_score_info):
        base64Frames, audio_path = BaselineModel.process_video(self, video_path=vid_path)
        prompt = FALL_DETECTION_PROMPT_WITH_SAFETY_SCORE.format(safety_score_info=safety_score_info)

        _, buffer = cv2.imencode(".jpg", segmented_image)
        base64Image = base64.b64encode(buffer).decode("utf-8")
        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": [
                "These are the frames from the video.",
                *map(lambda x: {"type": "image_url", 
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames),
                
                "This is the image used as context for the safety score.",
                {"type": "image_url", "image_url": {
                    "url": f"data:image/png;base64,{base64Image}"}
                }
                ],
            }
            ],
            temperature=0,
        )

        return response.choices[0].message.content
    
    def eval_consistency(self, vid_path, frames, description):
        base64Frames = BaselineModel.process_certain_frames(self, video_path=vid_path, frames=frames)
        base64Frames = BaselineModel.process_certain_frames(self, video_path=vid_path, frames=frames)
        prompt = "Your job is to determine whether the following description and explanation are consistent with what happens in a video. "
        prompt += "The description was generated by another AI model, which got the same set of frames as you will. "
        prompt += "Output a confidence score between 0 and 1, where 0.000 indicates a description completely inconsistent with the frames, 1.000 indicates a thorough and accurate description of the given frames and any score under 0.500 indicates a lack of understanding of the frames. "
        prompt += "Decimals are allowed up to 3 decimal places. Then, justify your confidence score. "
        prompt += "Finally, based on the description generated and the video, determine whether the person has fallen, representing your answer with either the letter Y or N at the end of your response. "
        prompt += "Here is the description: "
        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
            {"role": "system", "content": prompt + description},
            {"role": "user", "content": [
                "These are the frames from the video.",
                *map(lambda x: {"type": "image_url", 
                                "image_url": {"url": f'data:image/jpg;base64,{x}', "detail": "low"}}, base64Frames)
                ],
            }
            ],
            temperature=0,
        )

        print("Response Received.")

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
    
    def predict_custom_safety(self, directory, vidnums):
        video_paths = load_vids(directory)
        predictions = []
        # print(video_paths, len(video_paths))
        # print(vidnums, len(vidnums))  

        for n in vidnums:
            video_path = video_paths[n - 1]
            result_image, safety_score_info = get_safety_score_info(video_path)
            cv2.imwrite('result_image_from_video.jpg', result_image)
            output = self.get_safety_score_response(vid_path=video_paths[n - 1], segmented_image=result_image, safety_score_info=safety_score_info)
            predictions.append(output)

        return predictions

class VideoLLaVA:
    def __init__(self, model_name="Video-LLaVA"):
        self.model_name = model_name

    def get_response(self, video_path, client=None):
        if not client:
            print("need to make client :(")
            client = Client("http://127.0.0.1:7860")
        prompt = "USER: <video>The person in the video is either performing an Activity of Daily Life or falls in the video. Determine whether or not the person in the chronological series of images, which were extracted from a video, has fallen. Explain why you think the person has or has not fallen. ASSISTANT:"
        try:
            output = client.predict(
                prompt=prompt,
                video_path={"video":handle_file(video_path)},
                api_name="/predict",
            )
            return output
        except requests.exceptions.RequestException as e:
            print("Error:", e)

    def get_safety_score_response(self, video_path, segmented_image, safety_score_info):
        if not client:
            print("need to make client :(")
            client = Client("http://127.0.0.1:7860")
        prompt = "USER: <video>" + FALL_DETECTION_PROMPT_WITH_SAFETY_SCORE.format(safety_score_info=safety_score_info) + " ASSISTANT:"
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
            output = self.get_response(video_path=video_paths[n - 1], client=client)
            predictions.append(output)

        return predictions
        
    def predict_custom_safety(self, directory, vidnums):
        video_paths = load_vids(directory)
        predictions = []

        for n in vidnums:
            video_path = video_paths[n - 1]
            result_image, safety_score_info = get_safety_score_info(video_path)
            cv2.imwrite('result_image_from_video.jpg', result_image)
            output = self.get_safety_score_response(vid_path=video_paths[n - 1], segmented_image=result_image, safety_score_info=safety_score_info)
            predictions.append(output)

        return predictions

# model = BaselineModel()

# ans = model.eval_consistency("./data/Videos/video_(4).avi", [0, 25, 50, 75, 100, 125, 150, 175, 200], "The person has not fallen. They appear to have intentionally laid down on the mattress placed on the floor. The sequence of movements suggests a deliberate action rather than an accidental fall.")
# print(ans)

# print("Confidence score" + re.search("[01][.][0-9]+", ans).group())

if __name__ == "__main__":
    model = VideoLLaVA()
    vid_directory = './data/Videos/'

    responses = model.predict_custom_safety(vid_directory, [1])
    print(responses)