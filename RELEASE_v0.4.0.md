# Release v0.4.0 - Debug Dashboard

**Release Date:** January 5, 2026

## 🎉 New Features

### Browser-Based Debug Dashboard
Added a comprehensive debug dashboard accessible via browser to monitor and inspect API requests in real-time.

**Features:**
- **📡 Request History**: View all HTTP requests with method badges, status codes, and response times
- **🔒 Variables Tab**: Monitor stored variables (auth tokens, etc.)
- **📊 Statistics Dashboard**: Real-time stats showing total requests, successes, and errors
- **🎨 Syntax-Highlighted JSON**: Colorized JSON responses with proper formatting
  - Keys in blue, strings in orange, numbers in green, booleans/null in blue
  - Proper line breaks and indentation
  - Word wrapping for long values
- **⏱️ Relative Timestamps**: Shows "X sec ago", "X min ago" for each request, auto-updating every 2 seconds
- **🔄 Auto-Refresh**: Dashboard updates every 2 seconds without page reload
- **📱 Expandable Responses**: Click requests to expand/collapse full JSON responses
- **🌐 Server Info**: Displays current OpenAPI server, URL, and endpoint count

**Access:**
- Dashboard URL is exposed via `get_server_info` tool in the `debug_ui_url` field
- Automatically starts on a free port when the MCP server launches
- Example: `http://localhost:PORT`

**Technical Details:**
- Simple HTTP server running on daemon thread
- No external CDN dependencies (custom inline syntax highlighter)
- Stores last 50 requests in memory
- Updates only changed DOM elements for performance

## 🛠️ Improvements

- **Enhanced `get_server_info`**: Now includes `debug_ui_url` field pointing to the debug dashboard
- **Request Logging**: All API requests are automatically logged to the debug UI
- **Context Integration**: Dashboard shows current server configuration and stats
- **Error Tracking**: Failed requests (4xx, 5xx, network errors) are tracked separately

## 📋 Technical Implementation

**Files Added:**
- `src/debug_server.py` - Debug server with embedded HTML/CSS/JavaScript

**Files Modified:**
- `src/main.py` - Initialize and start debug server
- `src/request_executor.py` - Log all requests to debug UI
- `src/context_manager.py` - Store debug URL
- `src/tools.py` - Expose debug URL in `get_server_info`

## 🎯 Use Cases

1. **Development & Testing**: Monitor API requests while building integrations
2. **Debugging**: Inspect request/response payloads without checking logs
3. **Token Management**: Verify stored authentication tokens
4. **Performance Monitoring**: Track response times across requests
5. **Error Investigation**: Quickly identify failed requests and review error responses

## 🚀 Getting Started

After starting the MCP server:
1. Call `get_server_info` to get the `debug_ui_url`
2. Open the URL in your browser
3. Make API requests - they'll appear automatically in the dashboard
4. Click on any request to expand and view the full JSON response
5. Switch to Variables tab to see stored auth tokens

## 📝 Notes

- Dashboard is read-only (view requests, cannot modify or replay)
- Request history persists until server restart
- Timestamps update in real-time based on client-side calculation
- JSON syntax highlighting works without external dependencies
- All emojis rendered as HTML entities for cross-browser compatibility

---

**Previous Release:** v0.3.1 (Query Parameter Bug Fix)
