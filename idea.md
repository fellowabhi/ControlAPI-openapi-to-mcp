# OpenAPI MCP Server - Technical Design Document

## Project Structure
```
openapi-mcp-server/
├── src/
│   ├── main.py              # MCP server entry point
│   ├── openapi_loader.py    # OpenAPI JSON fetcher/parser
│   ├── request_executor.py  # HTTP request handler
│   ├── variable_manager.py  # Variable storage/substitution
│   └── tools.py             # MCP tool definitions
├── config.json              # Server configuration
├── pyproject.toml           # Dependencies
└── README.md
```

## Configuration (config.json)
```json
{
  "openapi_url": "http://localhost:8000/openapi.json",
  "refresh_interval": 300
}
```

## Core Modules

### 1. openapi_loader.py
**Purpose:** Fetch and parse OpenAPI spec

**Class: `OpenAPILoader`**
- `__init__(url: str)`
- `load() -> dict` - Fetch JSON from URL
- `get_endpoints() -> List[Endpoint]` - Extract all endpoints
- `get_endpoint_schema(path: str, method: str) -> dict` - Get specific endpoint details
- `search_endpoints(query: str) -> List[Endpoint]` - Search by path/description/tag

**Endpoint dataclass:**
```python
@dataclass
class Endpoint:
    path: str
    method: str
    summary: str
    description: str
    tags: List[str]
    parameters: dict
    request_body: dict
    responses: dict
```

### 2. variable_manager.py
**Purpose:** Manage runtime variables and template substitution

**Class: `VariableManager`**
- `__init__()`
- `set(key: str, value: str)` - Store variable
- `get(key: str) -> str` - Retrieve variable
- `get_all() -> dict` - List all variables
- `substitute(text: str) -> str` - Replace `{{var}}` with values (regex-based)
- `apply_to_request(headers: dict, body: any, path: str) -> tuple` - Apply substitution to all request parts

**Storage:** Simple in-memory dict

### 3. request_executor.py
**Purpose:** Execute HTTP requests

**Class: `RequestExecutor`**
- `__init__(variable_manager: VariableManager, base_url: str)`
- `execute(path: str, method: str, headers: dict, query_params: dict, path_params: dict, body: any) -> Response` - Make HTTP call with variable substitution

**Response dataclass:**
```python
@dataclass
class Response:
    status_code: int
    headers: dict
    body: any
    elapsed_ms: float
```

**Implementation:** Use `httpx.Client` for requests

### 4. tools.py
**Purpose:** Define MCP tools

**Tools:**

1. **list_endpoints**
   - Input: `{"method_filter": "GET", "path_prefix": "/api", "tag": "users"}`
   - Returns: List of matching endpoints with path, method, summary

2. **execute_request**
   - Input: `{"path": "/api/users/{id}", "method": "GET", "path_params": {"id": "123"}, "query_params": {}, "headers": {}, "body": null}`
   - Returns: Response object as JSON

3. **set_variable**
   - Input: `{"key": "auth_token", "value": "Bearer xyz..."}`
   - Returns: Success confirmation

4. **get_variables**
   - Input: `{}`
   - Returns: All stored variables

5. **search_schema**
   - Input: `{"query": "user login"}`
   - Returns: Matching endpoints

**Each tool calls corresponding loader/executor/manager methods**

### 5. main.py
**Purpose:** MCP server initialization

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Initialize components
loader = OpenAPILoader(config["openapi_url"])
loader.load()
var_manager = VariableManager()
executor = RequestExecutor(var_manager, base_url)

# Create MCP server
server = Server("openapi-mcp")

# Register tools from tools.py
register_tools(server, loader, executor, var_manager)

# Run server
async def main():
    async with stdio_server() as streams:
        await server.run(
            streams[0], streams[1], 
            server.create_initialization_options()
        )
```

## Dependencies (pyproject.toml)
```toml
[project]
name = "openapi-mcp-server"
dependencies = [
    "mcp>=0.9.0",
    "httpx>=0.27.0",
    "pydantic>=2.0.0"
]
```

## Variable Substitution Logic
- Scan strings for `{{variable_name}}` pattern
- Replace with value from VariableManager
- Apply to: headers, body (JSON stringified), query params, path params
- Example: `Authorization: {{auth_token}}` → `Authorization: Bearer abc123`

## Error Handling
- Wrap all HTTP calls in try/except
- Return structured errors: `{"error": "message", "type": "NetworkError"}`
- Validate endpoint exists before execution
- Validate required parameters from OpenAPI schema

## Startup Flow
1. Load config.json
2. Fetch OpenAPI JSON from URL
3. Parse into Endpoint objects
4. Initialize MCP server with 5 tools
5. Ready to accept tool calls

## Example AI Workflow
```
AI: list_endpoints(method_filter="POST", tag="auth")
→ Returns login endpoint

AI: execute_request(path="/api/auth/login", method="POST", body={"user":"admin","pass":"123"})
→ Returns token

AI: set_variable(key="token", value="Bearer xyz...")
→ Stored

AI: execute_request(path="/api/users", method="GET", headers={"Authorization":"{{token}}"})
→ Auto-substitutes token, returns users
```

## Implementation Notes
- Keep it synchronous for simplicity (async only for MCP server loop)
- No caching initially - reload OpenAPI on each server start
- Base URL extracted from OpenAPI `servers[0].url` or config
- Use regex `r'\{\{(\w+)\}\}'` for variable substitution

**Total LOC estimate: ~400-500 lines**