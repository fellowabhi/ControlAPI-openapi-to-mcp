# Release v0.5.0

## Debug UI Enhancements
- Collapsible sections with ▶/▼ toggles for Request Body, Params, Headers, and Response
- Auto-expand latest request with all non-empty sections visible
- Hide empty JSON sections to reduce clutter
- Better visual separation with bordered containers

## Bug Fixes
- Fixed request/response misalignment (responses were showing for wrong requests)
- Added complete request logging (body, params, headers were missing)
- Fixed auto-run.sh stdout pollution causing MCP JSON errors in VS Code

## New Features
- Custom debug port via `DEBUG_PORT` env var (default: 45133)
- Graceful fallback if port unavailable - won't block server startup
- Debug UI status/error shown in `get_server_info` response

## Usage
```json
"env": {
  "DEBUG_PORT": "45133"
}
```

Access debug UI at `http://localhost:45133` (or your custom port)
