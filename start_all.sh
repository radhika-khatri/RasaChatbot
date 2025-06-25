#!/bin/bash
echo "🌐 Starting FastAPI on port 8000..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

sleep 2

echo "🤖 Starting Rasa Actions Server..."
rasa run actions --port 5055 --debug
