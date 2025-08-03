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

The server is pre-configured with the following settings:
- `INFLECTRA_SPIRA_BASE_URL`: `https://jimballic.spiraservice.net/`
- `INFLECTRA_SPIRA_USERNAME`: `auser`

You need to provide your own API key. Open the file `src/mcp_server_spiraplan/utils/spira_client.py` and replace the placeholder `"REPLACE_WITH_YOUR_API_KEY"` with your actual Spira API key. The user password for testing is `D3vop$1`.
