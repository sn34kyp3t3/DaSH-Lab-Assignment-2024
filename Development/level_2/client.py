import requests
import json
import time
import sys
from datetime import datetime
from dotenv import load_dotenv
import os


load_dotenv(".env-dev")

# Read the prompts from input.txt
with open("../input.txt", "r") as file:
    prompts = file.readlines()

# Strip any extra whitespace or newlines from the prompts
prompts = [prompt.strip() for prompt in prompts]

# Local - Server URL
server_endpoint = "http://127.0.0.1:5000"


def send_prompt(prompt, client_id, server_url=server_endpoint):
    response = requests.post(
        f"{server_url}/api/generate", json={"prompt": prompt, "client_id": client_id}
    )
    return response.json()


def write_response_to_file(filename, data):
    with open(filename, "a") as f:
        json.dump(data, f)
        f.write("\n")  # Write each response on a new line


def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_url> <prompt_file> <client_id>")
        sys.exit(1)

    server_url = os.getenv("SERVER_URL")
    client_id = os.getenv("CLIENT_ID")
    output_file = f"./client_outputs/output_{client_id}.json"

    for prompt in prompts:
        prompt = prompt.strip()
        time_sent = int(time.time())

        # Send prompt to server
        response_data = send_prompt(server_url, prompt, client_id)

        # Modify response to include received time
        response_data["TimeSent"] = time_sent
        response_data["TimeRecvd"] = int(time.time())

        # Write the response to a file
        write_response_to_file(output_file, response_data)

        # Optional: Delay between sending requests
        time.sleep(5)  # Adjust delay to fit rate limits and testing needs


if __name__ == "__main__":
    main()
