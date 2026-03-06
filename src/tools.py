from typing import Any, Optional
from dataclasses import asdict

from mcp.server import Server
from mcp.types import Tool, TextContent

from .openapi_loader import OpenAPILoader
from .request_executor import RequestExecutor
from .variable_manager import VariableManager
from .context_manager import ContextManager
from .output_utils import (
    compact_json, paginate, filter_fields,
    apply_jsonpath, format_endpoint_compact,
    format_schema_compact, format_response,
)


def register_tools(
    server: Server,
    loader: OpenAPILoader,
    executor: RequestExecutor,
    var_manager: VariableManager,
    context: ContextManager,
):
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="list_endpoints",
                description="List API endpoints. Returns compact one-liners default (saves tokens). Use compact=false for full details. Supports pagination with limit/offset.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "method_filter": {"type": "string", "description": "Filter by HTTP method (GET, POST, etc.)"},
                        "path_prefix": {"type": "string", "description": "Filter by path prefix"},
                        "tag": {"type": "string", "description": "Filter by tag"},
                        "limit": {"type": "integer", "description": "Results per page (default: 10)", "default": 10},
                        "offset": {"type": "integer", "description": "Starting index for pagination (default: 0)", "default": 0},
                        "compact": {"type": "boolean", "description": "If true (default), return one-liner per endpoint. If false, return full JSON objects.", "default": True},
                    },
                },
            ),
            Tool(
                name="execute_request",
                description="Execute HTTP requests to API endpoints. Returns compact response by default (no headers, no server_context). Use include_headers/include_server_context for full details. Supports JSONPath filtering on response body via jsonpath param. Full unfiltered response is always cached — use replay_response to re-inspect without re-executing.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "API path, use exactly as listed in the spec (e.g., '/api/v1/users/')"},
                        "method": {"type": "string", "description": "HTTP method"},
                        "path_params": {"type": "object", "description": "Path parameters"},
                        "query_params": {"type": "object", "description": "Query parameters"},
                        "headers": {"type": "object", "description": "Request headers"},
                        "body": {"type": "object", "description": "Request body as JSON object"},
                        "include_headers": {"type": "boolean", "description": "Include response headers (default: false)", "default": False},
                        "include_server_context": {"type": "boolean", "description": "Include server context in response (default: false)", "default": False},
                        "jsonpath": {"type": "string", "description": "JSONPath to filter the response body directly. Root $ = body root. e.g. '$.data.access_token' not '$.body.data.access_token'"},
                        "max_body_length": {"type": "integer", "description": "Max characters for response body. Truncates with ...[truncated] if exceeded."},
                    },
                    "required": ["path", "method"],
                },
            ),
            Tool(
                name="replay_response",
                description="Re-inspect a cached API response WITHOUT re-executing the request. Critical for POST/PUT/DELETE — avoids duplicate side effects. Supports JSONPath to drill into specific fields. Use index=-1 for latest (default), or negative index for older responses.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer", "description": "History index. -1=latest (default), -2=second latest, etc.", "default": -1},
                        "jsonpath": {"type": "string", "description": "JSONPath to filter the response body directly. Root $ = body root. e.g. '$.data.access_token' not '$.body.data.access_token'"},
                        "include_headers": {"type": "boolean", "description": "Include response headers (default: false)", "default": False},
                        "include_request": {"type": "boolean", "description": "Include the original request details (default: false)", "default": False},
                        "max_body_length": {"type": "integer", "description": "Max characters for response body"},
                    },
                },
            ),
            Tool(
                name="set_variable",
                description="Store values (like auth tokens) for reuse in requests via {{varname}} syntax",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Variable name"},
                        "value": {"type": "string", "description": "Variable value"},
                    },
                    "required": ["key", "value"],
                },
            ),
            Tool(
                name="get_variables",
                description="Get all stored variables",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="search_schema",
                description="Search endpoints by query (multiple words = OR match). Returns compact one-liners by default. Supports pagination with limit/offset.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query (space-separated words, matches ANY word)"},
                        "limit": {"type": "integer", "description": "Results per page (default: 10)", "default": 10},
                        "offset": {"type": "integer", "description": "Starting index (default: 0)", "default": 0},
                        "compact": {"type": "boolean", "description": "If true (default), return one-liners. If false, return full JSON.", "default": True},
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="reload_schema",
                description="Reload OpenAPI schema to get latest endpoints",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="get_endpoint_details",
                description="Get detailed schema for a specific endpoint. Returns compact field:type summary by default. Use compact=false for raw OpenAPI schema. Use sections to request only specific parts.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "API path"},
                        "method": {"type": "string", "description": "HTTP method (GET, POST, etc.)"},
                        "sections": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Request specific sections only: 'summary', 'parameters', 'request_body', 'responses', 'content_types'. Default: all.",
                        },
                        "compact": {"type": "boolean", "description": "If true (default), show compact field:type summary. If false, return raw OpenAPI schema including $refs. Use compact=false if compact shows empty body.", "default": True},
                    },
                    "required": ["path", "method"],
                },
            ),
            Tool(
                name="get_server_info",
                description="Get current server configuration and status. Returns debug_ui_url — if the user asks to open the debug monitor, fetch this then open that URL in their browser.",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="set_server_config",
                description="Connect to an OpenAPI server. If no server is configured yet, use this tool first to set the OpenAPI URL. Switches between different API servers dynamically.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "openapi_url": {"type": "string", "description": "OpenAPI schema URL (e.g., http://localhost:8000/openapi.json)"},
                        "base_url": {"type": "string", "description": "Optional base URL override. Auto-detected from spec by default — only set this if requests are hitting the wrong host/port."},
                        "nickname": {"type": "string", "description": "Optional friendly name for this server (e.g., 'Production', 'Local Dev')"},
                    },
                    "required": ["openapi_url"],
                },
            ),
            Tool(
                name="get_server_history",
                description="View recent server switches with timestamps and last operations",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="health_check",
                description="Test connectivity to current OpenAPI server",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        import json

        # Allow these tools even when schema is not loaded
        allowed_without_schema = [
            "reload_schema", "get_server_info", "set_server_config",
            "get_server_history", "health_check", "replay_response",
            "set_variable", "get_variables",
        ]
        
        if name not in allowed_without_schema and not loader.loaded:
            if loader.url == "not-configured":
                return [TextContent(type="text", text="No server configured yet. Use set_server_config to connect to an OpenAPI server, or ask the user for the OpenAPI URL.")]
            else:
                return [TextContent(type="text", text=f"Error: {loader.load_error}. Use set_server_config to switch servers or reload_schema to retry.")]

        # ── list_endpoints ──────────────────────────────────────────
        if name == "list_endpoints":
            endpoints = loader.get_endpoints()
            method_filter = arguments.get("method_filter", "").upper()
            path_prefix = arguments.get("path_prefix", "")
            tag = arguments.get("tag", "")

            if method_filter:
                endpoints = [e for e in endpoints if e.method == method_filter]
            if path_prefix:
                endpoints = [e for e in endpoints if e.path.startswith(path_prefix)]
            if tag:
                endpoints = [e for e in endpoints if tag in e.tags]

            # Build result objects
            result = []
            for e in endpoints:
                entry = {"path": e.path, "method": e.method, "summary": e.summary}
                if e.content_types:
                    entry["content_types"] = e.content_types
                result.append(entry)

            # Pagination
            limit = arguments.get("limit", 10)
            offset = arguments.get("offset", 0)
            page = paginate(result, limit, offset)

            compact = arguments.get("compact", True)
            if compact:
                lines = [f"[{context.get_display_name()}] Endpoints ({offset+1}-{min(offset+limit, page['total'])} of {page['total']}):"]
                for entry in page["results"]:
                    lines.append(format_endpoint_compact(entry))
                if page["has_more"]:
                    lines.append(f"(use offset={offset+limit} for next page)")
                return [TextContent(type="text", text="\n".join(lines))]
            else:
                output = {
                    "server": context.get_display_name(),
                    "endpoints": page["results"],
                    "total": page["total"],
                    "has_more": page["has_more"],
                }
                if page["has_more"]:
                    output["next_offset"] = offset + limit
                return [TextContent(type="text", text=compact_json(output))]

        # ── execute_request ─────────────────────────────────────────
        elif name == "execute_request":
            # Add warning if this is first request after server switch
            warning = ""
            if context.should_warn_first_request():
                info = context.get_info()
                warning = (
                    f"WARNING: First request to '{info['nickname']}' "
                    f"(Base: {info['base_url']}). Verify correct server.\n\n"
                )
            
            # Get preferred content type from schema
            schema_content_type = loader.get_preferred_content_type(
                arguments["path"],
                arguments["method"]
            )
            
            response = executor.execute(
                path=arguments["path"],
                method=arguments["method"],
                headers=arguments.get("headers"),
                query_params=arguments.get("query_params"),
                path_params=arguments.get("path_params"),
                body=arguments.get("body"),
                schema_content_type=schema_content_type,
            )
            
            # NOTE: Full unfiltered response is already stored in
            # DebugHandler.request_history by request_executor.py.
            # Below we only filter what the AI sees.
            
            # Build response dict with optional sections
            resp_dict = {"status_code": response.status_code}
            
            if arguments.get("include_headers", False):
                resp_dict["headers"] = response.headers
            
            # Response body — apply jsonpath if provided
            body = response.body
            jsonpath_expr = arguments.get("jsonpath")
            if jsonpath_expr and body:
                body = apply_jsonpath(body, jsonpath_expr)
            
            # Apply max body length truncation
            max_len = arguments.get("max_body_length")
            if max_len and body is not None:
                serialized = compact_json(body) if not isinstance(body, str) else body
                if len(serialized) > max_len:
                    body = serialized[:max_len] + "...[truncated]"
            
            resp_dict["body"] = body
            resp_dict["elapsed_ms"] = response.elapsed_ms
            
            if arguments.get("include_server_context", False):
                resp_dict["server_context"] = {
                    "openapi_url": context.current.openapi_url,
                    "base_url": context.current.base_url,
                    "nickname": context.get_display_name(),
                }
            
            return [TextContent(type="text", text=warning + compact_json(resp_dict))]

        # ── replay_response ─────────────────────────────────────────
        elif name == "replay_response":
            from .debug_server import DebugServer
            
            index = arguments.get("index", -1)
            cached = DebugServer.get_response(index)
            
            if cached is None:
                count = DebugServer.get_history_count()
                return [TextContent(type="text", text=compact_json({
                    "error": f"No cached response at index {index}",
                    "history_count": count,
                    "hint": "Use index=-1 for latest, -2 for second latest, etc."
                }))]
            
            # Build result
            result = {
                "method": cached["method"],
                "path": cached["path"],
                "status_code": cached["status"],
                "elapsed_ms": cached["elapsed_ms"],
            }
            
            if arguments.get("include_request", False):
                result["request_body"] = cached.get("request_body")
                result["request_headers"] = cached.get("request_headers")
                result["request_params"] = cached.get("request_params")
            
            if arguments.get("include_headers", False):
                # Note: response headers are not stored in debug history currently
                result["note"] = "Response headers are not stored in cache"
            
            # Response body — apply jsonpath if provided
            body = cached.get("response_body")
            jsonpath_expr = arguments.get("jsonpath")
            if jsonpath_expr and body:
                body = apply_jsonpath(body, jsonpath_expr)
            
            # Apply max body length
            max_len = arguments.get("max_body_length")
            if max_len and body is not None:
                serialized = compact_json(body) if not isinstance(body, str) else body
                if len(serialized) > max_len:
                    body = serialized[:max_len] + "...[truncated]"
            
            result["body"] = body
            
            return [TextContent(type="text", text=compact_json(result))]

        # ── set_variable ────────────────────────────────────────────
        elif name == "set_variable":
            var_manager.set(arguments["key"], arguments["value"])
            return [TextContent(type="text", text=f"Variable '{arguments['key']}' set successfully")]

        # ── get_variables ───────────────────────────────────────────
        elif name == "get_variables":
            return [TextContent(type="text", text=compact_json(var_manager.get_all()))]

        # ── search_schema ───────────────────────────────────────────
        elif name == "search_schema":
            endpoints = loader.search_endpoints(arguments["query"])
            result = []
            for e in endpoints:
                entry = {"path": e.path, "method": e.method, "summary": e.summary}
                if e.content_types:
                    entry["content_types"] = e.content_types
                result.append(entry)

            # Pagination
            limit = arguments.get("limit", 10)
            offset = arguments.get("offset", 0)
            page = paginate(result, limit, offset)

            compact = arguments.get("compact", True)
            if compact:
                lines = [f"Search '{arguments['query']}' ({offset+1}-{min(offset+limit, page['total'])} of {page['total']}):"]
                for entry in page["results"]:
                    lines.append(format_endpoint_compact(entry))
                if page["has_more"]:
                    lines.append(f"(use offset={offset+limit} for next page)")
                return [TextContent(type="text", text="\n".join(lines))]
            else:
                output = {
                    "query": arguments["query"],
                    "results": page["results"],
                    "total": page["total"],
                    "has_more": page["has_more"],
                }
                if page["has_more"]:
                    output["next_offset"] = offset + limit
                return [TextContent(type="text", text=compact_json(output))]

        # ── reload_schema ───────────────────────────────────────────
        elif name == "reload_schema":
            loader.reload()
            if loader.loaded:
                endpoint_count = len(loader.get_endpoints())
                context.update_load_status(is_loaded=True, endpoint_count=endpoint_count)
                return [TextContent(type="text", text=f"Schema reloaded. {endpoint_count} endpoints available.")]
            else:
                return [TextContent(type="text", text=compact_json({"error": loader.load_error}))]
        
        # ── get_endpoint_details ────────────────────────────────────
        elif name == "get_endpoint_details":
            schema = loader.get_endpoint_schema(arguments["path"], arguments["method"])
            if not schema:
                return [TextContent(type="text", text=f"Endpoint {arguments['method']} {arguments['path']} not found")]
            
            compact = arguments.get("compact", True)
            sections = arguments.get("sections")  # None = all sections
            
            if compact:
                # Build compact text summary
                lines = [f"{arguments['method'].upper()} {arguments['path']}"]
                
                summary = schema.get("summary", "")
                description = schema.get("description", "")
                
                if (not sections or "summary" in sections):
                    if summary:
                        lines.append(f"Summary: {summary}")
                    if description and description != summary:
                        lines.append(f"Description: {description}")
                
                # Content types
                request_body = schema.get("requestBody", {})
                if request_body and (not sections or "content_types" in sections):
                    content = request_body.get("content", {})
                    if content:
                        short_types = []
                        for ct in content.keys():
                            if "json" in ct:
                                short_types.append("json")
                            elif "form-urlencoded" in ct:
                                short_types.append("form")
                            elif "multipart" in ct:
                                short_types.append("multipart")
                            else:
                                short_types.append(ct)
                        lines.append(f"Content-Types: {', '.join(short_types)}")
                
                # Request body schema (compact)
                if request_body and (not sections or "request_body" in sections):
                    required = request_body.get("required", False)
                    lines.append(f"Body {'(required)' if required else '(optional)'}:")
                    content = request_body.get("content", {})
                    # Prefer JSON schema
                    body_schema = None
                    for ct in ["application/json", "application/x-www-form-urlencoded", "multipart/form-data"]:
                        if ct in content and "schema" in content[ct]:
                            body_schema = content[ct]["schema"]
                            break
                    if body_schema:
                        compact_schema = format_schema_compact(body_schema)
                        # Indent each line of schema
                        for line in compact_schema.split("\n"):
                            lines.append(f"  {line}")
                
                # Parameters (compact)
                parameters = schema.get("parameters", [])
                if parameters and (not sections or "parameters" in sections):
                    lines.append("Parameters:")
                    for param in parameters:
                        p_name = param.get("name", "?")
                        p_in = param.get("in", "?")
                        p_required = " (required)" if param.get("required") else ""
                        p_type = param.get("schema", {}).get("type", "any")
                        lines.append(f"  {p_name}: {p_type} (in: {p_in}){p_required}")
                
                # Responses (compact — just status codes and descriptions)
                responses = schema.get("responses", {})
                if responses and (not sections or "responses" in sections):
                    resp_parts = [f"{code}: {resp.get('description', '')}" for code, resp in responses.items()]
                    lines.append(f"Responses: {'; '.join(resp_parts)}")
                
                return [TextContent(type="text", text="\n".join(lines))]
            
            else:
                # Full raw schema (opt-in)
                details = {
                    "path": arguments["path"],
                    "method": arguments["method"].upper(),
                }
                
                if not sections or "summary" in sections:
                    details["summary"] = schema.get("summary", "")
                    details["description"] = schema.get("description", "")
                
                if not sections or "content_types" in sections:
                    request_body = schema.get("requestBody", {})
                    if request_body:
                        content = request_body.get("content", {})
                        details["content_types"] = list(content.keys())
                
                if not sections or "request_body" in sections:
                    request_body = schema.get("requestBody", {})
                    if request_body:
                        content = request_body.get("content", {})
                        details["request_body_required"] = request_body.get("required", False)
                        details["request_schemas"] = {}
                        for ct, ct_schema in content.items():
                            if "schema" in ct_schema:
                                details["request_schemas"][ct] = ct_schema["schema"]
                
                if not sections or "parameters" in sections:
                    parameters = schema.get("parameters", [])
                    if parameters:
                        details["parameters"] = parameters
                
                if not sections or "responses" in sections:
                    responses = schema.get("responses", {})
                    if responses:
                        details["responses"] = responses
                
                return [TextContent(type="text", text=compact_json(details))]

        # ── get_server_info ─────────────────────────────────────────
        elif name == "get_server_info":
            info = context.get_info()
            # Compact single JSON — no duplicate human-readable + JSON
            return [TextContent(type="text", text=compact_json(info))]

        # ── set_server_config ───────────────────────────────────────
        elif name == "set_server_config":
            new_url = arguments["openapi_url"]
            new_base = arguments.get("base_url")
            new_nickname = arguments.get("nickname")
            
            # Try to load new schema first
            temp_loader_url = loader.url
            loader.reload_with_url(new_url)
            
            # Update context with results
            if loader.loaded:
                # Only switch context if loading succeeded
                context.switch_server(new_url, new_base, new_nickname)
                
                endpoint_count = len(loader.get_endpoints())
                context.update_load_status(is_loaded=True, endpoint_count=endpoint_count)
                
                # Update executor base URL
                from .main import extract_base_url
                endpoint_paths = [e.path for e in loader.get_endpoints()[:10]]
                new_base_url = extract_base_url(new_url, loader.base_url, new_base or "", endpoint_paths)
                executor.base_url = new_base_url.rstrip("/")
                context.current.base_url = new_base_url
                
                return [TextContent(type="text", text=compact_json({
                    "status": "connected",
                    "nickname": context.get_display_name(),
                    "openapi_url": new_url,
                    "base_url": new_base_url,
                    "endpoints": endpoint_count,
                }))]
            else:
                # Restore old URL on failure (only if it was a valid URL)
                if temp_loader_url != "not-configured":
                    loader.reload_with_url(temp_loader_url)
                return [TextContent(type="text", text=compact_json({
                    "status": "error",
                    "error": loader.load_error,
                    "message": "Previous server configuration preserved.",
                }))]

        # ── get_server_history ──────────────────────────────────────
        elif name == "get_server_history":
            history = context.get_history()
            if not history:
                return [TextContent(type="text", text="No server history available.")]
            # Compact JSON — no duplicate display
            return [TextContent(type="text", text=compact_json(history))]

        # ── health_check ────────────────────────────────────────────
        elif name == "health_check":
            import httpx
            import time
            
            try:
                start = time.perf_counter()
                resp = httpx.get(context.current.openapi_url, timeout=10.0)
                elapsed = (time.perf_counter() - start) * 1000
                resp.raise_for_status()
                
                spec = resp.json()
                endpoint_count = 0
                for path_methods in spec.get("paths", {}).values():
                    endpoint_count += len([m for m in path_methods if m in ("get", "post", "put", "patch", "delete")])
                
                return [TextContent(type="text", text=compact_json({
                    "status": "healthy",
                    "server": context.get_display_name(),
                    "response_ms": round(elapsed, 2),
                    "endpoints": endpoint_count,
                    "http_status": resp.status_code,
                }))]
            except Exception as e:
                return [TextContent(type="text", text=compact_json({
                    "status": "unreachable",
                    "server": context.get_display_name(),
                    "error": str(e),
                }))]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]
