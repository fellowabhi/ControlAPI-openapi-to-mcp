from typing import Any, Optional
from dataclasses import asdict

from mcp.server import Server
from mcp.types import Tool, TextContent

from openapi_loader import OpenAPILoader
from request_executor import RequestExecutor
from variable_manager import VariableManager
from context_manager import ContextManager


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
                description="List API endpoints with optional filters",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "method_filter": {"type": "string", "description": "Filter by HTTP method"},
                        "path_prefix": {"type": "string", "description": "Filter by path prefix"},
                        "tag": {"type": "string", "description": "Filter by tag"},
                    },
                },
            ),
            Tool(
                name="execute_request",
                description="Execute HTTP requests to API endpoints. Use this for login, fetching data, and all API calls. Supports variable substitution with {{varname}}. For JSON payloads, pass body as an object (not a string).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "API path"},
                        "method": {"type": "string", "description": "HTTP method"},
                        "path_params": {"type": "object", "description": "Path parameters"},
                        "query_params": {"type": "object", "description": "Query parameters"},
                        "headers": {"type": "object", "description": "Request headers"},
                        "body": {"type": "object", "description": "Request body as JSON object, e.g., {\"email\": \"user@example.com\", \"password\": \"pass123\"}"},
                    },
                    "required": ["path", "method"],
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
                description="Search endpoints by query string",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
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
                description="Get detailed schema information for a specific endpoint including content-types, parameters, and request body schema",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "API path"},
                        "method": {"type": "string", "description": "HTTP method (GET, POST, etc.)"},
                    },
                    "required": ["path", "method"],
                },
            ),
            Tool(
                name="get_server_info",
                description="Get current server configuration and status. Use this to check which server you're connected to before making requests. Provides debug_ui_url for browser-based request/response monitoring (default port: 45133). If debug UI fails to start due to port conflict, debug_ui_error will indicate the issue.",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="set_server_config",
                description="Connect to an OpenAPI server. If no server is configured yet, use this tool first to set the OpenAPI URL. Switches between different API servers dynamically.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "openapi_url": {"type": "string", "description": "OpenAPI schema URL (e.g., http://localhost:8000/openapi.json)"},
                        "base_url": {"type": "string", "description": "Optional base URL override for API requests"},
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
        allowed_without_schema = ["reload_schema", "get_server_info", "set_server_config", "get_server_history", "health_check"]
        
        if name not in allowed_without_schema and not loader.loaded:
            if loader.url == "not-configured":
                return [TextContent(type="text", text="No server configured yet. Use set_server_config to connect to an OpenAPI server, or ask the user for the OpenAPI URL.")]
            else:
                return [TextContent(type="text", text=f"Error: {loader.load_error}. Use set_server_config to switch servers or reload_schema to retry.")]

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

            result = []
            for e in endpoints:
                entry = {"path": e.path, "method": e.method, "summary": e.summary}
                if e.content_types:
                    entry["content_types"] = e.content_types
                result.append(entry)
            
            header = f"[Server: {context.get_display_name()}]\n\n"
            return [TextContent(type="text", text=header + json.dumps(result, indent=2))]

        elif name == "execute_request":
            # Add warning if this is first request after server switch
            warning = ""
            if context.should_warn_first_request():
                info = context.get_info()
                warning = (
                    f"⚠️  WARNING: First request to new server '{info['nickname']}'\n"
                    f"OpenAPI: {info['openapi_url']}\n"
                    f"Base URL: {info['base_url']}\n"
                    f"Please verify this is the correct server before proceeding.\n\n"
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
            
            # Add server context to response
            resp_dict = asdict(response)
            resp_dict["server_context"] = {
                "openapi_url": context.current.openapi_url,
                "base_url": context.current.base_url,
                "nickname": context.get_display_name(),
            }
            
            return [TextContent(type="text", text=warning + json.dumps(resp_dict, indent=2))]

        elif name == "set_variable":
            var_manager.set(arguments["key"], arguments["value"])
            return [TextContent(type="text", text=f"Variable '{arguments['key']}' set successfully")]

        elif name == "get_variables":
            return [TextContent(type="text", text=json.dumps(var_manager.get_all(), indent=2))]

        elif name == "search_schema":
            endpoints = loader.search_endpoints(arguments["query"])
            result = []
            for e in endpoints:
                entry = {"path": e.path, "method": e.method, "summary": e.summary}
                if e.content_types:
                    entry["content_types"] = e.content_types
                result.append(entry)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "reload_schema":
            loader.reload()
            if loader.loaded:
                endpoint_count = len(loader.get_endpoints())
                context.update_load_status(is_loaded=True, endpoint_count=endpoint_count)
                return [TextContent(type="text", text=f"OpenAPI schema reloaded successfully. {endpoint_count} endpoints available.")]
        
        elif name == "get_endpoint_details":
            schema = loader.get_endpoint_schema(arguments["path"], arguments["method"])
            if not schema:
                return [TextContent(type="text", text=f"Endpoint {arguments['method']} {arguments['path']} not found")]
            
            # Extract key information
            details = {
                "path": arguments["path"],
                "method": arguments["method"].upper(),
                "summary": schema.get("summary", ""),
                "description": schema.get("description", ""),
            }
            
            # Add content-types if request body exists
            request_body = schema.get("requestBody", {})
            if request_body:
                content = request_body.get("content", {})
                details["content_types"] = list(content.keys())
                details["request_body_required"] = request_body.get("required", False)
                
                # Add schema for each content type
                details["request_schemas"] = {}
                for ct, ct_schema in content.items():
                    if "schema" in ct_schema:
                        details["request_schemas"][ct] = ct_schema["schema"]
            
            # Add parameters
            parameters = schema.get("parameters", [])
            if parameters:
                details["parameters"] = parameters
            
            return [TextContent(type="text", text=json.dumps(details, indent=2))]

        elif name == "get_server_info":
            info = context.get_info()
            display = (
                f"🔌 Current Server: {info['nickname']}\n"
                f"📍 OpenAPI URL: {info['openapi_url']}\n"
                f"🌐 Base URL: {info['base_url']}\n"
                f"📊 Status: {'✅ Loaded' if info['is_loaded'] else '❌ Not Loaded'}\n"
                f"📋 Endpoints: {info['endpoint_count']}\n"
            )
            if info['loaded_at']:
                display += f"⏰ Loaded At: {info['loaded_at']}\n"
            if info['last_request_at']:
                display += f"🔄 Last Request: {info['last_request_method']} {info['last_request_path']} at {info['last_request_at']}\n"
            if info['load_error']:
                display += f"⚠️  Error: {info['load_error']}\n"
            
            display += f"\n{json.dumps(info, indent=2)}"
            return [TextContent(type="text", text=display)]

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
                from main import extract_base_url
                new_base_url = extract_base_url(new_url, loader.base_url, new_base or "")
                executor.base_url = new_base_url.rstrip("/")
                context.current.base_url = new_base_url
                
                return [TextContent(type="text", text=(
                    f"✅ Successfully switched to '{context.get_display_name()}'\n"
                    f"📍 OpenAPI: {new_url}\n"
                    f"🌐 Base URL: {new_base_url}\n"
                    f"📋 Endpoints: {endpoint_count}\n\n"
                    f"⚠️  WARNING: You are now connected to a different server. "
                    f"Use get_server_info to verify the current configuration before making requests."
                ))]
            else:
                # Restore old URL on failure (only if it was a valid URL)
                if temp_loader_url != "not-configured":
                    loader.reload_with_url(temp_loader_url)
                return [TextContent(type="text", text=(
                    f"❌ Failed to load schema from new server\n"
                    f"Error: {loader.load_error}\n"
                    f"Previous server configuration has been preserved."
                ))]

        elif name == "get_server_history":
            history = context.get_history()
            if not history:
                return [TextContent(type="text", text="No server history available.")]
            
            display = "📜 Server Switch History (most recent first):\n\n"
            for i, ctx in enumerate(history, 1):
                display += (
                    f"{i}. {ctx['nickname']} - {ctx['openapi_url']}\n"
                    f"   Loaded: {ctx['loaded_at'] or 'Never'}, "
                    f"Endpoints: {ctx['endpoint_count']}\n\n"
                )
            
            display += f"\n{json.dumps(history, indent=2)}"
            return [TextContent(type="text", text=display)]

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
                
                return [TextContent(type="text", text=(
                    f"✅ Server '{context.get_display_name()}' is healthy\n"
                    f"📍 OpenAPI URL: {context.current.openapi_url}\n"
                    f"⚡ Response Time: {elapsed:.2f}ms\n"
                    f"📋 Endpoints Available: {endpoint_count}\n"
                    f"✅ Status: {resp.status_code}"
                ))]
            except Exception as e:
                return [TextContent(type="text", text=(
                    f"❌ Server '{context.get_display_name()}' is unreachable\n"
                    f"📍 OpenAPI URL: {context.current.openapi_url}\n"
                    f"❌ Error: {str(e)}"
                ))]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]
