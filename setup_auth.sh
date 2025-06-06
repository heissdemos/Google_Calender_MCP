#!/bin/bash

# Google Calendar OAuth Setup Script (Containerized)
# This script runs authentication setup in a container with GUI forwarding

echo "Google Calendar MCP Authentication Setup"
echo "========================================="

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo "❌ Error: credentials.json not found!"
    echo "Please download credentials.json from Google Cloud Console and place it in this directory."
    exit 1
fi

# Create data directory
mkdir -p data

# Check if token already exists
if [ -f "data/token.json" ]; then
    echo "✅ Token already exists in data/token.json"
    echo "If you need to re-authenticate, delete data/token.json and run this script again."
    exit 0
fi

echo "🔐 Starting OAuth authentication..."
echo "A browser window will open for Google authentication."
echo ""

# Run authentication in container with display forwarding
docker run --rm -it \
    -v "$(pwd):/app" \
    -v "$(pwd)/data:/app/data" \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -e TOKEN_FILE=/app/data/token.json \
    google-calendar-mcp \
    uv run python setup_auth.py

# Check if authentication was successful
if [ -f "data/token.json" ]; then
    echo ""
    echo "✅ Authentication successful!"
    echo "✅ Token saved to data/token.json"
    echo "✅ Google Calendar MCP is now ready to use with Claude"
else
    echo ""
    echo "❌ Authentication failed!"
    echo "Please try again or check your credentials.json file."
    exit 1
fi