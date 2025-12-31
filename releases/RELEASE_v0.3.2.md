# ControlAPI-MCP v0.3.2 - Content-Type Visibility & Critical Bugfix

## 🐛 Critical Bug Fixed

### Server Configuration Failure from Initial State

**Issue:** When starting fresh (no server configured yet), attempting to connect to a server would fail with:
```
Error: Request URL is missing an 'http://' or 'https://' protocol.
```

**Root Cause:** When `set_server_config` fails to load a new schema, it attempts to restore the previous server configuration by calling `loader.reload_with_url(temp_loader_url)`. However, on first run when no server is configured, `temp_loader_url` is `"not-configured"` (a placeholder string, not a valid URL). This caused httpx to fail when trying to fetch the schema.

**Fix:** Check if the previous URL is valid (`temp_loader_url != "not-configured"`) before attempting to reload it. If starting fresh and the new server fails to load, simply don't attempt a rollback.

**File changed:** `src/tools.py` (line 309)

## ✨ New Features

### 1. Content-Type Visibility in Endpoint Listings

Endpoint listings now show which content-types each endpoint accepts, making it clear when endpoints require special encoding:

```json
{
  "path": "/api/v1/auth/login",
  "method": "POST",
  "summary": "Login",
  "content_types": ["application/x-www-form-urlencoded"]
}
```

**Benefits:**
- AI agents can see content-type requirements at a glance
- Easier debugging of API integration issues
- Clear documentation of endpoint expectations

**Files changed:**
- `src/openapi_loader.py` - Added `content_types` field to `Endpoint` dataclass
- `src/tools.py` - Updated `list_endpoints` and `search_schema` to include content-types

### 2. New Tool: `get_endpoint_details`

Get comprehensive schema information for any endpoint:

```json
{
  "path": "/api/v1/auth/login",
  "method": "POST",
  "summary": "Login",
  "description": "Login user and return tokens with user data.",
  "content_types": ["application/x-www-form-urlencoded"],
  "request_body_required": true,
  "request_schemas": {
    "application/x-www-form-urlencoded": {
      "$ref": "#/components/schemas/Body_login_api_v1_auth_login_post"
    }
  },
  "parameters": [...]
}
```

**Features:**
- Shows all accepted content-types
- Indicates if request body is required
- Provides full request schema for each content-type
- Lists all parameters (path, query, header)

**File changed:** `src/tools.py` - Added new tool handler

### 3. Content-Type Auto-Detection (Enhanced Visibility)

Auto-detection was implemented in v0.3.0 but wasn't visible to AI agents. Now the schema information is exposed, making it clear:

- **Auto-sets** Content-Type from OpenAPI schema when not provided
- **Preserves** user-specified Content-Type headers
- **Works transparently** - no manual header configuration needed

**How it works:**
1. `openapi_loader.get_preferred_content_type()` extracts content-type from schema
2. Priority: `application/x-www-form-urlencoded` > `application/json` > first available
3. Auto-sets header only if: endpoint has body AND user hasn't specified Content-Type
4. Uses `httpx` `data=` for form encoding, `json=` for JSON

## 🔧 Technical Details

**Modified Files:**
- `src/openapi_loader.py` - Extract and expose content-types from schemas
- `src/tools.py` - Add endpoint details tool, expose content-types in listings, fix rollback bug
- `src/main.py` - Add debugpy remote debugging support (optional, via `MCP_DEBUG=1` env var)

**New Files:**
- `.vscode/launch.json` - Debugger configuration for MCP server

## 📋 Test Results

✅ **Initial server setup**: Connects successfully from unconfigured state  
✅ **Content-type visibility**: Login endpoint shows `application/x-www-form-urlencoded`  
✅ **Auto-detection**: Login works without manual Content-Type header  
✅ **User override**: Explicit Content-Type headers are preserved  
✅ **GET requests**: No Content-Type set when body is empty  
✅ **Detailed inspection**: `get_endpoint_details` returns complete schema info

## 🎯 Impact

**Before this release:**
- ❌ Could not configure server on first run
- ❌ Content-type requirements hidden from AI agents
- ❌ No way to inspect detailed endpoint schemas
- ❌ Auto-detection worked but wasn't documented/visible

**After this release:**
- ✅ Server configuration works seamlessly from fresh start
- ✅ Content-types visible in all endpoint listings
- ✅ Dedicated tool for detailed schema inspection
- ✅ Complete transparency of auto-detection behavior

## 🛠️ Development Tools Added

**Remote Debugging Support:**
- Set `MCP_DEBUG=1` environment variable in mcp.json
- Debugger listens on localhost:5678
- Use "Attach to MCP Server" launch configuration
- Helpful for troubleshooting complex MCP interactions

## 🙏 Acknowledgments

Thanks to the debugging session that uncovered the server configuration bug and led to improved content-type visibility!
