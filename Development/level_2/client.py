import requests
import json
import time
from dotenv import load_dotenv
import os
import logging

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("client.log"),
        logging.StreamHandler(),
    ],
)

load_dotenv("../../.env.local")
server_url = os.getenv("SERVER_URL")
client_id = os.getenv("CLIENT_ID")
output_file = f"./client_outputs/output_{client_id}.json"


def write_response_to_file(filename, data):
    logging.info(f"Writing response to {filename}")
    with open(filename, "a") as f:
        json.dump(data, f)
        f.write("\n")  # Write each response on a new line


def send_prompt(prompt):
    try:
        response = requests.post(
            f"{server_url}/api/generate",
            json={"prompt": prompt, "client_id": client_id},
        )

        if response.status_code != 200:
            logging.error(f"Failed to send prompt: {response_data}")

        response_data = response.json()
        logging.info(f"Prompt sent: {prompt}, Response: {response_data}")
    except Exception as e:
        logging.error(f"Error sending prompt: {prompt}, Error: {str(e)}")


def main():
    # Read the prompts from input.txt
    with open("../../input.txt", "r") as file:
        prompts = file.readlines()

    prompts = [prompt.strip() for prompt in prompts]

    for i, prompt in enumerate(prompts):
        logging.info(f"Sending prompt {i+1}/{len(prompts)}: {prompt}")
        send_prompt(prompt)
        time.sleep(2)  # Adjust delay to respect rate limits

    logging.info(f"Client {client_id} finished processing")


if __name__ == "__main__":
    main()
