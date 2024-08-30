from flask import Flask, request, jsonify
import anthropic
from dotenv import load_dotenv
import os
import time
import queue
import threading

load_dotenv(".env-dev")

app = Flask(__name__)

api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Client(api_key=api_key)
request_queue = queue.Queue()
clients = []


# call the LLM API with rate limiting
def call_llm_api(prompt):
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
    return response.content[0].text


# broadcast responses to all connected clients
def broadcast_to_clients(prompt, response):
    for client_socket in clients:
        client_socket.send(
            jsonify(
                {
                    "Prompt": prompt,
                    "Message": response,
                    "TimeSent": int(
                        time.time()
                    ),  # Assuming broadcast happens immediately
                    "TimeReceived": int(time.time()),
                    "Source": "Anthropic [Claude]",
                }
            ).data.decode("utf-8")
        )


# handle API calls with rate limiting
def process_queue():
    while True:
        if not request_queue.empty():
            prompt_data = request_queue.get()
            # Call the LLM API
            response = call_llm_api(prompt_data["prompt"])
            # Send response to all clients
            broadcast_to_clients(prompt_data["prompt"], response)
            # Sleep to ensure we respect rate limits
            time.sleep(12)  # e.g., waiting 12 seconds between calls


@app.route("/api/generate", methods=["POST"])
def generate_response():
    data = request.json
    prompt = data.get("prompt")  # type: ignore
    client_id = data.get("client_id")  # type: ignore

    time_sent = int(time.time())

    request_queue.put({"prompt": prompt, "client_id": client_id})

    return jsonify(
        {
            "status": "prompt received and queued",
            "TimeSent": time_sent,
        }
    )


# WebSocket handler to manage client connections (for broadcasting)
@app.route("/api/connect", methods=["POST"])
def connect_client():
    # Add a new client connection to the list
    client_socket = request.environ.get("wsgi.input")
    clients.append(client_socket)
    return jsonify({"status": "Client connected"})


if __name__ == "__main__":
    # Start the queue processing in a separate thread
    threading.Thread(target=process_queue, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
