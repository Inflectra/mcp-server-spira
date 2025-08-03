# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the entire project to the working directory
COPY . .

# Install dependencies using uv
RUN pip install uv
RUN uv pip install --system -e ".[dev]"

# Command to run the new SpiraPlan MCP server
CMD ["python", "-m", "mcp_server_spiraplan"]
