FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY calendar_mcp.py ./
COPY credentials.json ./
COPY setup_auth.py ./

# Create volume mount point for token persistence
VOLUME ["/app/data"]

# Set environment variable to store token in persistent volume
ENV TOKEN_FILE=/app/data/token.json

# Update the Python file to use the environment variable for token file
RUN sed -i "s|TOKEN_FILE = 'token.json'|TOKEN_FILE = os.environ.get('TOKEN_FILE', 'token.json')|" calendar_mcp.py

# Expose port for stdio transport (not needed but for documentation)
EXPOSE 8000

# Copy the runner script
COPY run_with_claude.py ./

# Run the MCP server with Claude integration
CMD ["uv", "run", "python", "run_with_claude.py"]