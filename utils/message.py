from firebase_admin import messaging

def create_message(data, tokens):
    message = messaging.MulticastMessage(
        tokens=tokens,
        android=messaging.AndroidConfig(
            priority='high'
        ),
        data=data
    )

    return message
