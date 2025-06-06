#!/bin/bash
# Wrapper script for Google Calendar MCP integration with Claude
# Usage: claude mcp add google-calendar ./google-calendar-mcp-wrapper.sh

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Create data directory for persistent token storage if it doesn't exist
mkdir -p data

# Run the Google Calendar MCP container in stdio mode
exec docker run --rm -i \
    -v "$SCRIPT_DIR/data:/app/data" \
    -e TOKEN_FILE=/app/data/token.json \
    google-calendar-mcp