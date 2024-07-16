import os
import cv2

def load_vids(directory_path):
    # extract sort video files by the value n in the "video_(n).avi" format
    video_files = sorted(
        [f for f in os.listdir(directory_path) if f.startswith("video") and f.endswith(".avi")],
        key=lambda x: int(x.split('_')[1].split('.')[0].strip('()'))
    )
    #list of video paths
    video_paths = []

    #get video paths from each video
    for file in video_files:
        video_paths.append(os.path.join(directory_path, file))
    
    return video_paths

def load_answer_files(directory_path):
    # extract sort text files by the value n in the "video_(n).txt" format
    text_files = sorted(
        [f for f in os.listdir(directory_path) if f.startswith("video") and f.endswith(".txt")],
        key=lambda x: int(x.split('_')[1].split('.')[0].strip('()'))
    )
    #list of text file paths
    text_paths = []

    #get text file paths from each text file
    for file in text_files:
        text_paths.append(os.path.join(directory_path, file))

    return text_paths

if __name__ == '__main__':
    print(load_vids('./src/pipeline/testing'))