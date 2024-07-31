import base64
import av
import cv2
import numpy as np

def get_video_frames(video_path):
    # Open the video file
    container = av.open(video_path)
    
    frames = []
    
    # Iterate over the frames in the video
    for frame in container.decode(video=0):
        # Convert the frame to an RGB image (NumPy array)
        img = frame.to_ndarray(format='rgb24')
        # Convert RGB to BGR for OpenCV
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        frames.append(img)
    
    return frames

def encode_image_to_base64(image):
    # Encode image to JPEG format
    _, buffer = cv2.imencode('.jpg', image)
    
    # Convert the buffer to a Base64 string
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return image_base64

def resize_video(input_path, output_path, width, height):
    # Open the input video file
    cap = cv2.VideoCapture(input_path)
    
    # Check if the video was successfully opened
    if not cap.isOpened():
        raise ValueError("Error opening video file")
    
    # Get the original video's properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Define the codec and create a VideoWriter object to save the resized video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while True:
        # Read a frame from the input video
        ret, frame = cap.read()
        
        # If no frame is returned, we've reached the end of the video
        if not ret:
            break
        
        # Resize the frame to the specified dimensions
        resized_frame = cv2.resize(frame, (width, height))
        
        # Write the resized frame to the output video
        out.write(resized_frame)
    
    # Release the video capture and writer objects
    cap.release()
    out.release()
    print(f"Video has been resized and saved to {output_path}")

if __name__ == "__main__":
    # Example usage
    video_path = 'video_1.avi'
    output_path = 'resized_video.avi'
    width = 640
    height = 480
    resize_video(video_path, output_path, width, height)
