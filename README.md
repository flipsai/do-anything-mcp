# Do Anything MCP - Model Context Protocol Integration

Do Anything MCP lets you upload and process any filetype through the Model Context Protocol.

## Features

- **Two-way communication**: Connect Claude AI to any application through a socket-based server
- **File Upload**: Upload and process any filetype
- **TTS**: Convert text to speech in any language
- **STT**: Convert speech to text in any language
- **Image Generation**: Generate images from text
- **Image Processing**: Process images in any format
- **Video Processing**: Process videos in any format
- **Audio Processing**: Process audio in any format
- **Document Processing**: Process documents in any format

## Components

The system consists of two main components:

1. **Do Anything MCP** (`src/do_anything_mcp/addon.py`): Connects to any application's API to send and receive commands
2. **MCP Server** (`src/do_anything_mcp/server.py`): A Python server that implements the Model Context Protocol and connects to any application

## Installation

### Prerequisites

- Python 3.8 or newer
- `uv` and `uvx` package managers:

   If you're on Mac:
   ```bash
   brew install uv
   pip install uvx
   ```
   
   On Windows:
   ```powershell
   # Install uv
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   set Path=C:\Users\username\.local\bin;%Path%
   
   # Install uvx
   pip install uvx
   ```
   
   On Linux:
   ```bash
   # Install uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install uvx
   pip install uvx
   ```
   
   Or visit [Install uv](https://github.com/astral-sh/uv) for other platforms

⚠️ **Do not proceed before installing UV and UVX**

### Claude for Desktop Integration

Go to Claude > Settings > Developer > Edit Config > `claude_desktop_config.json` to include the following:

```json
{
    "mcpServers": {
        "do-anything": {
            "command": "uvx",
            "args": [
                "do-anything-mcp"
            ]
        }
    }
}
```

### Cursor Integration

Run do-anything-mcp without installing it permanently through uvx. Go to Cursor Settings > MCP and paste this as a command:

```
uvx do-anything-mcp
```

⚠️ **Only run one instance of the MCP server (either on Cursor or Claude Desktop), not both**

TODO