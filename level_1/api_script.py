# from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
# import requests
# import json

# # Configuration
# API_KEY = "your_api_key_here"  # Replace with your API key
# API_URL = (
#     "https://api.your_llm_service.com/v1/generate"  # Replace with the actual API URL
# )


# # Function to make an API call
# def make_api_call(prompt):
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "prompt": prompt,
#         "max_tokens": 150,  # Customize as needed
#     }
#     response = requests.post(API_URL, headers=headers, json=data)
#     return response.json()


# # Read input from a text file
# with open("input.txt", "r") as file:
#     prompts = file.readlines()

# responses = []

# # Make API calls for each prompt and save the responses
# for prompt in prompts:
#     prompt = prompt.strip()
#     if prompt:
#         response = make_api_call(prompt)
#         responses.append(
#             {
#                 "prompt": prompt,
#                 "response": response,
#             }
#         )

# # Save the responses to a JSON file
# with open("responses.json", "w") as json_file:
#     json.dump(responses, json_file, indent=4)

# print("Responses saved to responses.json")

"""
import openai
import os
import pandas as pd
import time

openai.api_key = "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"


def get_completion(prompt, model="gpt-3.5-turbo"):

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

prompt = "what is openai ?"

response = get_completion(prompt)
print(response)
"""

import anthropic
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

with open("../input.txt", "r") as file:
    prompts = file.readlines()
    print(f"prompts: {prompts}")

prompts = [prompt.strip() for prompt in prompts]

source = "Claude"

responses = []

for prompt in prompts:
    time.sleep(12)
    print("sleeping for 12 seconds")
    time_sent = int(time.time())

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        system="You give brief and aappropriate answers.",  # optional
        messages=[
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    )

    time_received = int(time.time())

    message_content = message.content[0].text  # type:ignore
    print(message_content)

    responses.append(
        {
            "Prompt": prompt,
            "Message": message_content,
            "TimeSent": time_sent,
            "TimeReceived": time_received,
            "Source": source,
        }
    )

with open("output.json", "w") as json_file:
    json.dump(responses, json_file, indent=4)
