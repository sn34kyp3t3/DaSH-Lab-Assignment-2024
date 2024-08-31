from flask import Flask, request, jsonify
import anthropic
from dotenv import load_dotenv
import os
import time
import queue
import threading
import logging
import json

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),  # Save logs to a file
        logging.StreamHandler(),  # Print logs to console
    ],
)

load_dotenv("../../.env.local")

app = Flask(__name__)

api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Client(api_key=api_key)
request_queue = queue.Queue()
clients = {}  # Dictionary to store client ids and their output file paths

client_outputs_dir = "client_outputs"
if not os.path.exists(client_outputs_dir):
    os.makedirs(client_outputs_dir)
    logging.info(f"Created directory: {client_outputs_dir}")


def call_llm_api(prompt):
    try:
        logging.info(f"Sending request to LLM API with prompt: {prompt}")
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        )
        response_text = response.content[0].text
        logging.info(f"LLM API response: {response_text[0:10]}...")
        return response_text
    except Exception as e:
        logging.error(f"Error calling LLM API: {e}")
        return None  # Explicitly return None if there's an error


def process_queue():
    logging.info("Started processing queue.")
    while True:
        if not request_queue.empty():
            prompt_data = request_queue.get()
            logging.info(f"Dequeuing prompt data: {prompt_data}")

            prompt = prompt_data.get("prompt")
            client_id = prompt_data.get("client_id")
            time_sent = prompt_data.get("time_sent", int(time.time()))

            if not prompt:
                logging.warning("Received prompt data without prompt content.")
                continue

            logging.info(f"Calling LLM API with prompt: {prompt}")
            response = call_llm_api(prompt)

            if response:
                logging.info("Received response from LLM API")
                message_data = {
                    "Prompt": prompt,
                    "Message": response,
                    "TimeSent": time_sent,
                    "TimeReceived": int(time.time()),
                    "Source": "Claude",
                    "ClientID": client_id,
                }

                # Write response to all clients' output files
                for client_id, output_file in clients.items():
                    try:
                        # Read existing data
                        if os.path.exists(output_file):
                            with open(output_file, "r") as f:
                                data = json.load(f)
                        else:
                            data = []

                        # Append new response
                        data.append(message_data)

                        # Write updated data
                        with open(output_file, "w") as f:
                            json.dump(data, f, indent=4)

                        logging.info(f"Response written to file for client {client_id}")
                    except Exception as e:
                        logging.error(
                            f"Error writing to file for client {client_id}: {e}"
                        )

            else:
                logging.error("No response received from LLM API")

            # Sleep to ensure we respect rate limits
            time.sleep(12)  # Adjust this as per the API's rate limits


@app.route("/api/generate", methods=["POST"])
def generate_response():
    data = request.json
    prompt = data.get("prompt")
    client_id = data.get("client_id")

    time_sent = int(time.time())

    if client_id not in clients:
        clients[client_id] = f"{client_outputs_dir}/{client_id}_output.json"

    request_queue.put(
        {"prompt": prompt, "client_id": client_id, "time_sent": time_sent}
    )

    return jsonify(
        {
            "status": "prompt received and queued",
            "TimeSent": time_sent,
        }
    )


if __name__ == "__main__":
    # Start the queue processing in a separate thread
    threading.Thread(target=process_queue, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
