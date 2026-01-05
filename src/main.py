import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server

from openapi_loader import OpenAPILoader
from variable_manager import VariableManager
from request_executor import RequestExecutor
from context_manager import ContextManager
from tools import register_tools
from debug_server import DebugServer

# Remote debugging support
if os.getenv("MCP_DEBUG") == "1":
    import debugpy
    debugpy.listen(("localhost", 5678))
    print("Debugger listening on port 5678", flush=True)


def load_config() -> dict:
    openapi_url = os.getenv("OPENAPI_URL", "")
    
    return {
        "openapi_url": openapi_url,
        "refresh_interval": int(os.getenv("REFRESH_INTERVAL", "300")),
        "base_url": os.getenv("BASE_URL", ""),
        "server_nickname": os.getenv("SERVER_NICKNAME", "")
    }


def extract_base_url(openapi_url: str, loader_base_url: str, config_base_url: str) -> str:
    if config_base_url:
        return config_base_url
    if loader_base_url:
        return loader_base_url
    from urllib.parse import urlparse
    parsed = urlparse(openapi_url)
    return f"{parsed.scheme}://{parsed.netloc}"


async def main():
    config = load_config()
    
    # Initialize context manager with optional URL
    has_initial_config = bool(config["openapi_url"])
    
    context = ContextManager(
        openapi_url=config["openapi_url"] or "not-configured",
        base_url=config["base_url"] or None,
        nickname=config["server_nickname"] or None
    )
    
    # Only load if URL is configured
    if has_initial_config:
        loader = OpenAPILoader(config["openapi_url"])
        loader.load()
        
        # Update context with load results
        context.update_load_status(
            is_loaded=loader.loaded,
            endpoint_count=len(loader.get_endpoints()) if loader.loaded else 0,
            load_error=loader.load_error if not loader.loaded else None
        )
        
        base_url = extract_base_url(config["openapi_url"], loader.base_url, config["base_url"])
    else:
        # No initial config - start with empty loader
        loader = OpenAPILoader("not-configured")
        loader.loaded = False
        loader.load_error = "No server configured. Use set_server_config to connect to an API."
        base_url = "http://localhost:8000"
    
    var_manager = VariableManager()
    executor = RequestExecutor(var_manager, base_url, context)
    
    # Start debug server (with optional custom port from env)
    import os
    custom_port = os.getenv('DEBUG_PORT')
    if custom_port:
        try:
            custom_port = int(custom_port)
        except ValueError:
            custom_port = None
    
    debug = DebugServer(var_manager, context, custom_port)
    debug_port = debug.start()
    if debug_port:
        context.debug_url = f"http://localhost:{debug_port}"
    else:
        context.debug_url = None
        context.debug_error = debug.error_message
    
    server = Server("openapi-mcp")
    register_tools(server, loader, executor, var_manager, context)
    
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
