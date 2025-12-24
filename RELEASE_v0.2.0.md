# ControlAPI-MCP v0.2.0 - Dynamic Server Switching

## 🎯 Major Features

### Zero-Config Startup
- **No configuration required!** Start the server without any environment variables
- AI assistant guides you through setup interactively
- Simply click the one-click install link and go

### Dynamic Server Switching
- Connect to any OpenAPI server at runtime using `set_server_config`
- Switch between multiple environments (dev, staging, production)
- Each server maintains independent state and history
- Automatic schema reloading when switching

### Enhanced Server Management
**4 New Tools:**
- `get_server_info` - Check current server and connection status
- `set_server_config` - Connect to or switch OpenAPI servers
- `get_server_history` - View recent server switches with timestamps
- `health_check` - Test server connectivity and response time

### Improved Safety
- ⚠️ Warning displayed on first request after server switch
- Server context included in all `execute_request` responses
- Failed server switches preserve previous configuration
- Clear error messages guide users to correct actions

## 📋 Changes

### Added
- Dynamic server configuration without restart
- Server context manager with history tracking
- Health check for server connectivity testing
- Request tracking (method, path, timestamp)
- AI-guided setup flow for first-time users

### Changed
- `OPENAPI_URL` environment variable now optional
- Simplified one-click install (no env vars in URL)
- Enhanced tool descriptions for better AI understanding
- `execute_request` responses now include server context
- Error messages guide users to use `set_server_config`

### Improved
- README with dynamic configuration examples
- Zero-config workflow demonstration
- Better separation of server state and variables

## 🚀 Installation

**One-Click Install (No Config Needed):**
- [Install in VS Code](https://vscode.dev/redirect/mcp/install?name=controlapi-mcp&config=%7B%22type%22%3A%22stdio%22%2C%22command%22%3A%22bash%22%2C%22args%22%3A%5B%22-c%22%2C%22mkdir%20-p%20~/.local/bin/controlapi-mcp%20%26%26%20curl%20-fsSL%20https%3A//raw.githubusercontent.com/fellowabhi/ControlAPI-openapi-to-mcp/main/auto-run.sh%20-o%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20chmod%20%2Bx%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20~/.local/bin/controlapi-mcp/auto-run.sh%22%5D%7D)

## 📖 Example Workflow

```
# First time - no config needed
1. Install MCP server (one click)
2. AI detects no server configured
3. Use: set_server_config(openapi_url="http://localhost:8000/openapi.json")
4. Start making API requests

# Switching servers
1. set_server_config(openapi_url="http://staging-api.com/openapi.json", nickname="Staging")
2. Warning shown on first request
3. get_server_history() to see all switches
4. Switch back anytime with set_server_config()
```

## 🔧 Technical Details

- **New Module:** `src/context_manager.py` - Manages server context and history
- **Updated:** All core modules for context awareness
- **Version:** 0.2.0 (bumped from 0.1.0)
- **Binary Size:** ~16MB (Linux x86_64)

## 🙏 Thanks

Special thanks to all contributors and testers who helped make this release possible!

---

**Full Changelog:** https://github.com/fellowabhi/ControlAPI-openapi-to-mcp/compare/v0.1.0...v0.2.0
