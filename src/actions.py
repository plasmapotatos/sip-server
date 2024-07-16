from utils.message import create_message
from firebase_admin import messaging

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
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        tokens=[token],
        android=messaging.AndroidConfig(
            priority='high'
        )
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
