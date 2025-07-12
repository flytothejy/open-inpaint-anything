#!/bin/bash

# Inpaint Anything FastAPI Development Server Start Script

echo "Starting Inpaint Anything FastAPI Development Server..."

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Warning: No virtual environment detected. Consider activating your venv."
fi

# Check if required models exist
if [ ! -f "./pretrained_models/sam_vit_h_4b8939.pth" ]; then
    echo "Warning: SAM model not found at ./pretrained_models/sam_vit_h_4b8939.pth"
    echo "You may need to download the model or set USE_MOCK_SERVICE=true"
fi

if [ ! -d "./pretrained_models/big-lama" ]; then
    echo "Warning: LaMa model not found at ./pretrained_models/big-lama"
    echo "You may need to download the model or set USE_MOCK_SERVICE=true"
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "No .env file found. Using default settings."
    echo "Consider copying .env.example to .env and configuring it."
fi

# Start the server
echo "Starting uvicorn server..."
uvicorn api.main:app --reload --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}