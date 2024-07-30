from datetime import datetime
import os
import subprocess
from time import sleep
from utils.message import create_message
from firebase_admin import messaging
from utils.request_utils import get_transcription

def speak(message, desired_volume, token):
    print(f"Speaking: {message}")
    data = {
        'action': 'speak',
        'message': message,
        'desiredVolume': str(desired_volume) if desired_volume else '5'
    }
    print(data)
    speak_message = create_message(data, [token])
    response = messaging.send_multicast(speak_message)
    print('Successfully sent message:', response)

def call(number, token):
    print(f"Calling {number}...")
    if number == "911":
        print("Cannot call 911 using the Firebase Cloud Messaging API.")
        return
    data = {
        'action': 'call',
        'phoneNumber': number
    }
    call_message = create_message(data, [token])
    response = messaging.send_multicast(call_message)
    print('Successfully sent message:', response)

def push_notification(title, body, token):
    print(f"Push Notification: {title} - {body}")
    data = {
        'action': 'push_notification',
        'title': title,
        'body': body
    }
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        tokens=[token],
        android=messaging.AndroidConfig(
            priority='high'
        ),
        data=data
    )
    response = messaging.send_multicast(message)

    print("Successfully sent notification:", response)

def vibrate(duration, token):
    print(f"Vibrating for {duration} ms")
    data = {
        'action': 'vibrate',
        'duration': duration
    }
    vibrate_message = create_message(data, [token])
    response = messaging.send_multicast(vibrate_message)
    print('Successfully sent message:', response)

def listen_for_feedback(duration):
    integer_duration = float(duration)
    sleep(integer_duration)
    RTSP_URL = "rtsp://169.233.172.175:8554/cam_with_audio"
    response_path = "./response"
    os.makedirs(response_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(response_path, f"clip_{timestamp}.mp4")

    print("Listening for feedback...")
    ffmpeg_command = [
        "ffmpeg",
        "-i", RTSP_URL,
        "-t", "5",
        "-c", "copy",
        filename
    ]

    # Execute FFmpeg command
    subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    transcription = get_transcription(filename)

    # This function would listen for feedback from the user, but we'll just print a message here
    print("Transcription:", transcription)
    return transcription
