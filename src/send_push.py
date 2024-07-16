import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

def send_push_notification(server_key, device_tokens, title, body, data=None):
    cred = credentials.Certificate(server_key)
    firebase_admin.initialize_app(cred)

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        tokens=device_tokens,
        android=messaging.AndroidConfig(
            priority='high'
        )
    )
    if data:
        message.data = data

    response = messaging.send_multicast(message)

    print("Successfully sent notification:", response)

# Replace with the path to your service account key JSON file
server_key = 'fir-pushnotifications-17c1a-firebase-adminsdk-2gn9p-192b0078c5.json'

# Replace with your device tokens
device_tokens = [
    'cA-0fbQARrO2ijGZ1UExle:APA91bEb0FCWo9QMu_eSuL7MhJSDsdsRJQiqlBifoQgRyouUnqxtPbYamiMpMy2_azJcWl3yg8LsfbusWWWJImwA6_F02-2dN1WufQXJ17oF3rz2kxsNr_4-v-GPfx_KFcelDe-XdbZs',
    # Add more device tokens as needed
]

# Notification details
title = 'Test Notification'
body = 'This is a test notification.'
data = {
    'action': 'call',
    'phoneNumber': '6692524341'
}

# Send push notification
send_push_notification(server_key, device_tokens, title, body, data)