import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('fir-pushnotifications-17c1a-firebase-adminsdk-2gn9p-192b0078c5.json')
firebase_admin.initialize_app(cred)

# Define the message
device_tokens = [
    'cA-0fbQARrO2ijGZ1UExle:APA91bEb0FCWo9QMu_eSuL7MhJSDsdsRJQiqlBifoQgRyouUnqxtPbYamiMpMy2_azJcWl3yg8LsfbusWWWJImwA6_F02-2dN1WufQXJ17oF3rz2kxsNr_4-v-GPfx_KFcelDe-XdbZs',
    'fFyqfZJWSUuNQS2cA1ec-A:APA91bGGQ-_r9xHje45dILAWkhRyiFOLyQvQslwy5zmE36yli0whteKozOpOQ81LMGo2ukmdwW534JViuf6P8SN0wkRumCcAQOd2Ephhj_CIU_yEUhRoe-QyyNEl34IQBdxc5UBOj3pd', # real
    'ec3oEqxpSmiaK2xfMIN8DN:APA91bFEbWfG8ruoEWy6f8KLv5ZJ5DiUT-5PAFIBCnBqZbYcuqSI7Wh-OXLsrVmyFQm11xKKoRpLuh1t6SLYn-9Splu-btn0yqzdfBromoGoE5wSI-HcSFO199rHp07wyea8BfS7UyoH' #ryan
]
message = messaging.MulticastMessage(
    tokens=device_tokens,
    android=messaging.AndroidConfig(
        priority='high'
    )
)
message.data = {
    'action': 'speak',
    # 'desiredVolume': '5',
    'phoneNumber': "6692524341",
    'message': 'hello',
    'duration': '1000',
}
# message = messaging.Message(
#     data = {
#         'action': 'speak',
#         'phoneNumber': '6692524341',
#         'message': 'hi'
#     },
#     token='cA-0fbQARrO2ijGZ1UExle:APA91bEb0FCWo9QMu_eSuL7MhJSDsdsRJQiqlBifoQgRyouUnqxtPbYamiMpMy2_azJcWl3yg8LsfbusWWWJImwA6_F02-2dN1WufQXJ17oF3rz2kxsNr_4-v-GPfx_KFcelDe-XdbZs'
# )
#real: 'fFyqfZJWSUuNQS2cA1ec-A:APA91bGgD67k1KRb5pvrS5ViX28ufl_lRzz8BjKqYqbk7iHnmknyboM6kB0gZC_pRbtb1kvaNdG6zmX9phfJCloRqD4mIOuZwwyvTyms9KdO0naZky-6ebpJ4SuVgMkaaSzZwcTrjgmy'

# Send the message
responses = messaging.send_multicast(message)

print('Successfully sent message:', responses.success_count, 'successes,', responses.failure_count, 'failures')
for response in responses.responses:
    if response.success:
        print('Successfully sent message:', response.message_id)
    else:
        print('Failed to send message:', response._exception)