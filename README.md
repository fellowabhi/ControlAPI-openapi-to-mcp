# ControlAPI-MCP

MCP server that exposes any OpenAPI/REST API as MCP tools with dynamic server switching and variable substitution.

## 🚀 One-Click Install

Click to install directly in your editor - **no configuration needed!**

**Linux / macOS:**

**[📥 Install in VS Code](https://vscode.dev/redirect/mcp/install?name=controlapi-mcp&config=%7B%22type%22%3A%22stdio%22%2C%22command%22%3A%22bash%22%2C%22args%22%3A%5B%22-c%22%2C%22mkdir%20-p%20~/.local/bin/controlapi-mcp%20%26%26%20curl%20-fsSL%20https%3A//raw.githubusercontent.com/fellowabhi/ControlAPI-openapi-to-mcp/main/auto-run.sh%20-o%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20chmod%20%2Bx%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20~/.local/bin/controlapi-mcp/auto-run.sh%22%5D%7D)**

**[📥 Install in VS Code Insiders](https://insiders.vscode.dev/redirect/mcp/install?name=controlapi-mcp&config=%7B%22type%22%3A%22stdio%22%2C%22command%22%3A%22bash%22%2C%22args%22%3A%5B%22-c%22%2C%22mkdir%20-p%20~/.local/bin/controlapi-mcp%20%26%26%20curl%20-fsSL%20https%3A//raw.githubusercontent.com/fellowabhi/ControlAPI-openapi-to-mcp/main/auto-run.sh%20-o%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20chmod%20%2Bx%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20~/.local/bin/controlapi-mcp/auto-run.sh%22%5D%7D)**

> 💡 **After Installation:** The AI assistant will guide you to connect to an API server. Simply provide the OpenAPI URL when asked, or use the `set_server_config` tool to connect to your API.

## Quick Start (Auto-Download)

**Zero installation** - automatically downloads and runs the latest release:

1. Download the auto-run script:
```bash
curl -O https://raw.githubusercontent.com/fellowabhi/ControlAPI-openapi-to-mcp/main/auto-run.sh
chmod +x auto-run.sh
```

2. Use it in your MCP config:
```json
{
  "servers": {
    "controlapi-mcp": {
      "type": "stdio",
      "command": "/path/to/auto-run.sh"
    }
  }
}
```

> Note: You can optionally set `OPENAPI_URL`, `BASE_URL`, and `SERVER_NICKNAME` in env vars, or configure dynamically using the `set_server_config` tool.

Download from [releases](https://github.com/fellowabhi/ControlAPI-openapi-to-mcp/releases) or build:

```bash
export OPENAPI_URL='http://your-api.com/openapi.json'
export BASE_URL='http://your-api.com'  # optional
./dist/controlapi-mcp
```

## Setup (Development)

```bash
pip install -e .
```

## Building Binary

```bash
./build.sh
```

Creates a standalone executable at `dist/controlapi-mcp` (16MB)

## MCP Configuration

### Using Binary

```json
{
  "servers": {
    "controlapi-mcp": {
      "type": "stdio",
      "command": "/path/to/openapi-mcp-adapter/dist/controlapi-mcp",
      "env": {
        "OPENAPI_URL": "http://localhost:8000/openapi.json",
        "BASE_URL": "http://localhost:8000",
        "DEBUG_PORT": "45133"
      }
    }
  }
}
```

### Using Python (Development)

```json
{
  "servers": {
    "controlapi-mcp": {
      "type": "stdio",
      "command": "/path/to/project/.venv/bin/python",
      "args": ["-m", "src.main"],
      "cwd": "/path/to/project",
      "env": {
        "OPENAPI_URL": "http://localhost:8000/openapi.json",
        "REFRESH_INTERVAL": "300",
        "PYTHONPATH": "/path/to/project",
        "BASE_URL": "http://localhost:8000",
        "DEBUG_PORT": "45133"
      }
    }
  }
}
```

**Optional:** `OPENAPI_URL`, `BASE_URL`, `SERVER_NICKNAME`, `DEBUG_PORT` (default: 45133)

> 💡 **No Configuration Needed:** You can start with no environment variables and configure the server dynamically using the `set_server_config` tool. The AI assistant will guide you through the setup.

> 🔍 **Debug UI:** Access browser-based request/response monitor at `http://localhost:45133` (or custom `DEBUG_PORT`). URL available in `get_server_info` response.

## Features

### Cross-Platform Support
- **Linux** (x86_64) - Full support
- **macOS** (Intel & Apple Silicon) - Full support
- **Windows** - Use Python or WSL

### Dynamic Server Switching
- Connect to any OpenAPI server at runtime
- Switch between multiple APIs (dev, staging, production)
- Server context tracking with history
- Automatic schema reloading

### Available Tools

- `set_server_config` - Connect to an OpenAPI server (use this first if not configured)
- `get_server_info` - Check current server and connection status
- `get_server_history` - View recent server switches
- `health_check` - Test server connectivity
- `list_endpoints` - List all API endpoints
- `search_schema` - Search endpoints by keyword
- `execute_request` - Make HTTP requests with variable substitution
- `set_variable` - Store variable (e.g., auth token)
- `get_variables` - View all stored variables
- `reload_schema` - Reload current server's schema

## Variable Substitution

Use `{{variable_name}}` in headers, body, or path:

```json
{
  "headers": {
    "Authorization": "{{token}}"
  }
}
```

## Example Workflow

1. **First time:** `set_server_config` with openapi_url
2. `execute_request` to `/auth/login` → get token
3. `set_variable` key="token" value="Bearer xyz..."
4. `execute_request` with `Authorization: {{token}}`
5. **Switch servers:** `set_server_config` to test on different environment

## Xquik OpenAPI to MCP

ControlAPI can expose Xquik's documented REST operations as MCP tools without
claiming that the Xquik platform itself is open source.

Connect ControlAPI with `set_server_config`:

```json
{
  "openapi_url": "https://xquik.com/openapi.json",
  "base_url": "https://xquik.com",
  "nickname": "Xquik"
}
```

Store the API key for request substitution:

```json
{
  "key": "xquik_api_key",
  "value": "<your Xquik API key>"
}
```

Then call a read operation through `execute_request`:

```json
{
  "path": "/api/v1/x/tweets/search",
  "method": "GET",
  "headers": {
    "x-api-key": "{{xquik_api_key}}"
  },
  "query_params": {
    "q": "agent research",
    "limit": 20
  }
}
```

Keep keys out of committed configuration and shared logs. ControlAPI redacts
credential-bearing headers from its debug history.

- Xquik docs: <https://docs.xquik.com>
- Xquik OpenAPI: <https://xquik.com/openapi.json>

Xquik is an independent third-party service. Not affiliated with X Corp.
"Twitter" and "X" are trademarks of X Corp.
