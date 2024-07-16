import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from src.actions import speak, call, push_notification

with open("output/gpt4o_output_20240716-161342.txt", "r") as output_file:
    response = output_file.read()
function_calls = re.findall(r'(\w+)\((.*?)\)', response)
token = 'fFyqfZJWSUuNQS2cA1ec-A:APA91bGgD67k1KRb5pvrS5ViX28ufl_lRzz8BjKqYqbk7iHnmknyboM6kB0gZC_pRbtb1kvaNdG6zmX9phfJCloRqD4mIOuZwwyvTyms9KdO0naZky-6ebpJ4SuVgMkaaSzZwcTrjgmy'

cred = credentials.Certificate('fir-pushnotifications-17c1a-firebase-adminsdk-2gn9p-192b0078c5.json')
firebase_admin.initialize_app(cred)

print(function_calls)
for func_name, args in function_calls:
    new_args = f"{args}, '{token}'"  # Add the token to the arguments
    exec(f"{func_name}({new_args})")