import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('fir-pushnotifications-17c1a-firebase-adminsdk-2gn9p-192b0078c5.json')
firebase_admin.initialize_app(cred)

# Define the message
message = messaging.Message(
    data = {
        'action': 'sms',
        'phoneNumber': '6692524341',
        'message': 'hi'
    },
    token='cA-0fbQARrO2ijGZ1UExle:APA91bEb0FCWo9QMu_eSuL7MhJSDsdsRJQiqlBifoQgRyouUnqxtPbYamiMpMy2_azJcWl3yg8LsfbusWWWJImwA6_F02-2dN1WufQXJ17oF3rz2kxsNr_4-v-GPfx_KFcelDe-XdbZs'
)
#real: 'fFyqfZJWSUuNQS2cA1ec-A:APA91bGgD67k1KRb5pvrS5ViX28ufl_lRzz8BjKqYqbk7iHnmknyboM6kB0gZC_pRbtb1kvaNdG6zmX9phfJCloRqD4mIOuZwwyvTyms9KdO0naZky-6ebpJ4SuVgMkaaSzZwcTrjgmy'

# Send the message
response = messaging.send(message)

print('Successfully sent message:', response)