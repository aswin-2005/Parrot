from groq import Groq
import ollama
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_MODEL = "openai/gpt-oss-120b"
OLLAMA_MODEL = "dolphin-mistral:7b"


USE_CLOUD = 1

client = Groq(api_key=os.getenv("GROG_API_KEY"))

def generate_response_cloud(messages):
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=GROQ_MODEL
    )
    return chat_completion.choices[0].message.content

def generate_response_local(messages):
    response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
    return response["message"]["content"]

def generate_response(messages):
    if USE_CLOUD:
        return generate_response_cloud(messages)
    else:
        return generate_response_local(messages)