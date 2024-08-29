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
