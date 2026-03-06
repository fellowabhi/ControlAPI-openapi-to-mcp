import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server

from src.openapi_loader import OpenAPILoader
from src.variable_manager import VariableManager
from src.request_executor import RequestExecutor
from src.context_manager import ContextManager
from src.tools import register_tools
from src.debug_server import DebugServer

# Remote debugging support
if os.getenv("MCP_DEBUG") == "1":
    try:
        import debugpy
        debugpy.listen(("localhost", 5679))
        print("Debugger listening on port 5679", flush=True)
    except RuntimeError:
        # Already listening, ignore
        pass


def load_config() -> dict:
    openapi_url = os.getenv("OPENAPI_URL", "")
    
    return {
        "openapi_url": openapi_url,
        "refresh_interval": int(os.getenv("REFRESH_INTERVAL", "300")),
        "base_url": os.getenv("BASE_URL", ""),
        "server_nickname": os.getenv("SERVER_NICKNAME", "")
    }


def extract_base_url(openapi_url: str, loader_base_url: str, config_base_url: str, endpoint_paths: list = None) -> str:
    if config_base_url:
        return config_base_url
    if loader_base_url:
        from urllib.parse import urlparse
        parsed = urlparse(loader_base_url)
        server_path = parsed.path.rstrip("/")
        # Detect double-path: servers[0].url has a path prefix (e.g. /api/v1)
        # but endpoint paths in the spec also start with that same prefix.
        # This is a common DRF / drf-spectacular pattern where the spec is misconfigured.
        # Fix: use just the origin so paths resolve correctly.
        if server_path and server_path != "/" and endpoint_paths:
            duplicate = any(
                p == server_path or p.startswith(server_path + "/")
                for p in endpoint_paths[:10]
            )
            if duplicate:
                return f"{parsed.scheme}://{parsed.netloc}"
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
        
        endpoint_paths = [e.path for e in loader.get_endpoints()[:10]] if loader.loaded else []
        base_url = extract_base_url(config["openapi_url"], loader.base_url, config["base_url"], endpoint_paths)
        # Update context with the actual resolved base_url
        context.current.base_url = base_url
    else:
        # No initial config - start with empty loader
        loader = OpenAPILoader("not-configured")
        loader.loaded = False
        loader.load_error = "No server configured. Use set_server_config to connect to an API."
        base_url = ""
        context.current.base_url = base_url
    
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
