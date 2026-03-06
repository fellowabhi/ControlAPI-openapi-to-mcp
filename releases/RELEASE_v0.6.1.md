# Release v0.6.1

## Debug Console Improvements
- Server info bar now shows Base URL, Schema URL, load status, and last request details
- Sidebar (Requests / Variables) is collapsed by default — click ☰ to toggle
- Fixed `debug_ui_url` disappearing from `get_server_info` after `set_server_config` calls

## Tool Description Improvements
- `execute_request`: AI is now nudged to always use `jsonpath` when response structure is predictable, saving tokens and avoiding re-execution
- `get_endpoint_details`: warns to use `compact=false` if body is empty (due to `$ref`)
- `set_server_config`: clarifies `base_url` is auto-detected and only needed as override

## Docs
- Added `docs/how_to_release.md` with release procedure
