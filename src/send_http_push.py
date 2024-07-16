import requests
import json

def send_push_notification(device_token, title, body):
    # FCM server endpoint
    url = 'https://fcm.googleapis.com/v1/projects/fir-pushnotifications-17c1a/messages:send'

    # Your server key obtained from the Firebase console
    server_key = 'AIzaSyDHYxzO-UpRm2HRgWoMHFjHi889qGpNNSQ'

    # Headers for the request
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + server_key,
    }

    # Payload for the request
    payload = {
        'to': device_token,
        'notification': {
            'title': title,
            'body': body,
        },
        'data': {
            'key1': 'value1',
            'key2': 'value2',
        }
    }

    # Sending the request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Checking the response
    if response.status_code == 200:
        print('Notification sent successfully')
    else:
        print('Failed to send notification')
        print(response.status_code)
        print(response.text)

# Example usage
device_token = 'cA-0fbQARrO2ijGZ1UExle:APA91bEb0FCWo9QMu_eSuL7MhJSDsdsRJQiqlBifoQgRyouUnqxtPbYamiMpMy2_azJcWl3yg8LsfbusWWWJImwA6_F02-2dN1WufQXJ17oF3rz2kxsNr_4-v-GPfx_KFcelDe-XdbZs'
title = 'Hello'
body = 'World'
send_push_notification(device_token, title, body)
