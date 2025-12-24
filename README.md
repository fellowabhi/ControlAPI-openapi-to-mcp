# ControlAPI-MCP

MCP server that exposes any OpenAPI/REST API as MCP tools with variable substitution.

## 🚀 One-Click Install

Click to install directly in your editor:

**[📥 Install in VS Code](https://vscode.dev/redirect/mcp/install?name=controlapi-mcp&config=%7B%22type%22%3A%22stdio%22%2C%22command%22%3A%22bash%22%2C%22args%22%3A%5B%22-c%22%2C%22mkdir%20-p%20~/.local/bin/controlapi-mcp%20%26%26%20curl%20-fsSL%20https%3A//raw.githubusercontent.com/fellowabhi/ControlAPI-openapi-to-mcp/main/auto-run.sh%20-o%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20chmod%20%2Bx%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20~/.local/bin/controlapi-mcp/auto-run.sh%22%5D%2C%22env%22%3A%7B%22OPENAPI_URL%22%3A%22http%3A//your-api.com/openapi.json%22%2C%22BASE_URL%22%3A%22http%3A//your-api.com%22%7D%7D)**

**[📥 Install in VS Code Insiders](https://insiders.vscode.dev/redirect/mcp/install?name=controlapi-mcp&config=%7B%22type%22%3A%22stdio%22%2C%22command%22%3A%22bash%22%2C%22args%22%3A%5B%22-c%22%2C%22mkdir%20-p%20~/.local/bin/controlapi-mcp%20%26%26%20curl%20-fsSL%20https%3A//raw.githubusercontent.com/fellowabhi/ControlAPI-openapi-to-mcp/main/auto-run.sh%20-o%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20chmod%20%2Bx%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20~/.local/bin/controlapi-mcp/auto-run.sh%22%5D%2C%22env%22%3A%7B%22OPENAPI_URL%22%3A%22http%3A//your-api.com/openapi.json%22%2C%22BASE_URL%22%3A%22http%3A//your-api.com%22%7D%7D)**

> 💡 **Installation Tip:** When VS Code prompts you, choose **"Install in Workspace"** instead of globally. This allows you to configure different `OPENAPI_URL` and `BASE_URL` for each project in your workspace's `.vscode/mcp.json` file.

> ⚠️ **After Installation:** Update the environment variables in `.vscode/mcp.json` to point to your specific API, for example:
> ```json
> "env": {
>   "OPENAPI_URL": "http://localhost:8000/openapi.json",
>   "BASE_URL": "http://localhost:8000"
> }
> ```

## Quick Start (Auto-Download)

**Zero installation** - automatically downloads and runs the latest release:

1. Download the auto-run script:
```bash
curl -O https://raw.githubusercontent.com/fellowabhi/ControlAPI-openapi-to-mcp/main/auto-run.sh
chmod +x auto-run.sh
```

2. Use it in your MCP config - it will auto-download the binary on first run:
```json
{
  "servers": {
    "controlapi-mcp": {
      "type": "stdio",
      "command": "/path/to/auto-run.sh",
      "env": {
        "OPENAPI_URL": "http://your-api.com/openapi.json",
        "BASE_URL": "http://your-api.com"
      }
    }
  }
}
```

## Quick Start (Manual Binary)

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
        "BASE_URL": "http://localhost:8000"
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
        "BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Required:** `OPENAPI_URL`, `PYTHONPATH`  
**Optional:** `REFRESH_INTERVAL` (default: 300), `BASE_URL` (overrides OpenAPI spec servers)

## Tools

- `list_endpoints` - List all API endpoints
- `search_schema` - Search endpoints by keyword
- `execute_request` - Make HTTP requests
- `set_variable` - Store variable (e.g., auth token)
- `get_variables` - View all stored variables

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

1. `execute_request` to `/auth/login` → get token
2. `set_variable` key="token" value="Bearer xyz..."
3. `execute_request` with `Authorization: {{token}}`
