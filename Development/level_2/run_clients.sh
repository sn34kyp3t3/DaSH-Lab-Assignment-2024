#!/bin/bash
source .env-dev
# Start the Flask server in the background
echo "Starting Flask server..."
python server.py &

sleep 2

# Launch multiple clients in parallel
echo "Starting clients..."
# Start clients based on the client IDs listed in .env
IFS=',' read -ra CLIENT_IDS <<<"$CLIENT_IDS"

for CLIENT_ID in "${CLIENT_IDS[@]}"; do
    CLIENT_ID=$CLIENT_ID python client.py &
done

wait

# Wait for all background jobs to complete
wait

echo "All clients have finished."
