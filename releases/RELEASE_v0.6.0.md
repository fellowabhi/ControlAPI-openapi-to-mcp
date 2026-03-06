# ControlAPI-MCP v0.6.0 - Token-Efficient Output & JSONPath Filtering

## ✨ New Features

### 1. Compact Output by Default
All tools now return compact JSON (no whitespace) to minimize token usage. Every tool is leaner by default.

### 2. Pagination for `list_endpoints` and `search_schema`
Both tools now support `limit` (default: 10) and `offset` parameters. Results include a `(use offset=N for next page)` hint.

### 3. JSONPath Filtering on Responses
`execute_request` and `replay_response` now accept a `jsonpath` parameter to extract specific fields from the response body directly.

```
jsonpath: "$.data.access_token"   →  returns just the token string
jsonpath: "$.results[*].id"       →  returns array of IDs
```

> Note: `$` is the body root — use `$.field` not `$.body.field`.

### 4. New Tool: `replay_response`
Re-inspect any cached API response without re-executing the request. Critical for POST/PUT/DELETE to avoid duplicate side effects.

- `index=-1` → latest response (default)
- `index=-2` → second latest, etc.
- Supports `jsonpath`, `include_headers`, `include_request`, `max_body_length`

### 5. `get_endpoint_details` Compact Mode
Endpoint details now default to a compact `field: type` summary instead of raw OpenAPI JSON. Use `compact=false` to get the full raw schema (including `$ref`s).

### 6. Debug Monitor Auto-Port Fallback
If the configured debug port (or default 45133) is occupied, the server now automatically falls back to an OS-assigned free port. The actual URL is always reported in `get_server_info` as `debug_ui_url`.

### 7. Auto-Detect Double-Path Bug
Many Django/DRF specs (drf-spectacular) set `servers[0].url` to include a path prefix (e.g. `http://localhost:8000/api/v1`) while endpoint paths also start with `/api/v1`. The adapter now auto-detects this and strips the duplicate prefix, so requests resolve correctly without any manual `base_url` override.

## 🐛 Bug Fixes

- **Falsy body check** — `if body` incorrectly skipped sending `0`, `false`, or `[]`. Fixed to `if body is not None`.
- **`base_url` display null** — `get_server_info` showed `null` for `base_url` on startup even though requests worked correctly.
- **Multi-word `search_schema`** — Queries like `"login orders"` now match endpoints containing ANY of the words (OR logic) instead of requiring the full phrase.
- **`reload_schema` missing return** — On failure, the tool fell through to "Unknown tool" instead of returning the error.
- **Hardcoded localhost fallback** — When no server is configured, `base_url` is now empty instead of silently defaulting to `http://localhost:8000`.

## 🛠️ Improved Tool Descriptions

Tool parameter descriptions updated to prevent common AI mistakes:
- `jsonpath`: explicitly states `$` = body root (not `$.body.*`)
- `get_endpoint_details` `compact`: warns to use `compact=false` if body appears empty (due to `$ref`)
- `set_server_config` `base_url`: clarifies it's auto-detected and only needed for overrides
- `get_server_info`: instructs AI to open `debug_ui_url` in browser when user asks for debug monitor
