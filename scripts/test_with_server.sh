#!/bin/bash

# Test script that starts server and runs tests

echo "🚀 Starting server and running CPU tests..."

# Function to cleanup background processes
cleanup() {
    echo "🧹 Cleaning up background processes..."
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
    fi
    exit
}

# Set up cleanup on script exit
trap cleanup EXIT INT TERM

# Start server in background
echo "📡 Starting FastAPI server in background..."
source venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
SERVER_PID=$!

echo "🔄 Server PID: $SERVER_PID"
echo "⏳ Waiting for server to start (15 seconds)..."
sleep 15

# Check if server is still running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "❌ Server failed to start. Check server.log"
    cat server.log
    exit 1
fi

echo "✅ Server appears to be running"

# Test health endpoint quickly
echo "🔍 Quick health check..."
if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo "✅ Server is responding"
else
    echo "❌ Server not responding to health check"
    echo "📋 Server log (last 20 lines):"
    tail -20 server.log
    exit 1
fi

# Run the CPU test
echo "🧪 Running CPU tests..."
python test_cpu_simple.py

echo "📋 Server log (last 20 lines):"
tail -20 server.log

echo "✅ Test completed"