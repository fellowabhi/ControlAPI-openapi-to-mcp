from typing import Any, Optional
from dataclasses import asdict

from mcp.server import Server
from mcp.types import Tool, TextContent

from openapi_loader import OpenAPILoader
from request_executor import RequestExecutor
from variable_manager import VariableManager


def register_tools(
    server: Server,
    loader: OpenAPILoader,
    executor: RequestExecutor,
    var_manager: VariableManager,
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
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        import json

        # Skip schema check for reload_schema tool
        if name != "reload_schema" and not loader.loaded:
            return [TextContent(type="text", text=f"Error: {loader.load_error}. Make sure the API server is running at {loader.url}, then use reload_schema tool to retry loading the OpenAPI specification.")]

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

            result = [{"path": e.path, "method": e.method, "summary": e.summary} for e in endpoints]
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "execute_request":
            response = executor.execute(
                path=arguments["path"],
                method=arguments["method"],
                headers=arguments.get("headers"),
                query_params=arguments.get("query_params"),
                path_params=arguments.get("path_params"),
                body=arguments.get("body"),
            )
            return [TextContent(type="text", text=json.dumps(asdict(response), indent=2))]

        elif name == "set_variable":
            var_manager.set(arguments["key"], arguments["value"])
            return [TextContent(type="text", text=f"Variable '{arguments['key']}' set successfully")]

        elif name == "get_variables":
            return [TextContent(type="text", text=json.dumps(var_manager.get_all(), indent=2))]

        elif name == "search_schema":
            endpoints = loader.search_endpoints(arguments["query"])
            result = [{"path": e.path, "method": e.method, "summary": e.summary} for e in endpoints]
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "reload_schema":
            loader.reload()
            if loader.loaded:
                endpoint_count = len(loader.get_endpoints())
                return [TextContent(type="text", text=f"OpenAPI schema reloaded successfully. {endpoint_count} endpoints available.")]
            else:
                return [TextContent(type="text", text=f"Failed to reload schema: {loader.load_error}")]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]
