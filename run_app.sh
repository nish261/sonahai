#!/bin/bash
# This script starts both the backend and frontend servers with a single command.

# Function to clean up the background backend process on exit
cleanup() {
    echo "\nShutting down backend server..."
    # The PIDs of background jobs are stored in $!
    kill $BACKEND_PID
    exit
}

# Trap the EXIT signal (e.g., when you press Ctrl+C) to run the cleanup function
trap cleanup EXIT

echo "🚀 Starting FastAPI backend server in the background..."
# Activate venv, start the backend server in the background (`&`), and store its PID
source /Users/nishchalasri/venv/bin/activate
uvicorn backend:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Backend started with PID: $BACKEND_PID"
echo "\nWaiting 5 seconds for the backend to initialize...\n"
sleep 5

echo "🚀 Starting Streamlit frontend UI..."
# Start the frontend in the foreground. The script will stay on this line until you close Streamlit.
streamlit run subdomain_scanner_ui.py
