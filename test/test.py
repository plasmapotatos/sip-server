import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from src.actions import speak, call, push_notification
from src.ffmpeg_server import chat_with_client, build_conversation
from utils.prompts import CONVERSATION_PROMPT

agent = []
client = []

conversation = build_conversation(agent, client)
prompt = CONVERSATION_PROMPT.format(conversation=conversation)
#print(prompt)

response = chat_with_client(agent, client)

#print(response)