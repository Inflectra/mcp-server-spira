# SpiraPlan MCP Server

This is a self-contained MCP server for SpiraPlan.

## Running with Docker

To build and run this server as a Docker container, follow these steps:

1.  **Build the Docker image:**
    From the root of the project, run the following command:
    ```bash
    docker build -t mcp-server-spiraplan .
    ```

2.  **Run the Docker container:**
    After building the image, run the following command to start the server:
    ```bash
    docker run -p 8000:8000 mcp-server-spiraplan
    ```
    The server will be accessible at `http://localhost:8000`.

## Configuration

To run the server, you need to create a `.env` file in the root of the project with the following variables:

```
INFLECTRA_SPIRA_BASE_URL=https://jimballic.spiraservice.net/
INFLECTRA_SPIRA_USERNAME=auser
INFLECTRA_SPIRA_API_KEY=D3vop$1
```

Replace `D3vop$1` with your actual Spira API Key (RSS Token).
