#!/bin/bash
# TMA Magic execution script

# Ensure path includes standard binaries (crucial for background launching)
# /opt/homebrew/bin is for Apple Silicon, /usr/local/bin for Intel
export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH

# 1. Navigate to project root
cd "/Users/john/Projects/test/TMA Project"

# 2. Activate virtualenv
source .venv/bin/activate

# 3. SELF-HEALING: Kill anything on port 8501
echo "🧹 Checking for zombie processes..."
PID=$(lsof -ti:8501)
if [ ! -z "$PID" ]; then
  echo "💀 Killing zombie process $PID on port 8501..."
  kill -9 $PID
fi

# 4. Start Streamlit in background
echo "🚀 Starting Streamlit Server..."
streamlit run app.py --server.port 8501 --server.headless true &
SERVER_PID=$!

# 5. Wait for server to be ready (dumb wait + check)
echo "⏳ Waiting for server to boot..."
sleep 2

# Poll for port active
for i in {1..10}; do
    if lsof -i:8501 >/dev/null; then
        echo "✅ Server is UP!"
        break
    fi
    echo "   ...still waiting ($i/10)"
    sleep 1
done

# 6. Launch Browser
echo "🌐 Opening Browser..."
open "http://localhost:8501"

# 7. Keep process alive to monitor server
echo "----------------------------------------"
echo "✅ TMA MAGIC IS RUNNING (PID: $SERVER_PID)"
echo "----------------------------------------"
echo "Press [Ctrl+C] to stop, or just close this window."
wait $SERVER_PID

