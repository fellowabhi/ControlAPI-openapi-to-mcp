import asyncio
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server

from openapi_loader import OpenAPILoader
from variable_manager import VariableManager
from request_executor import RequestExecutor
from tools import register_tools


def load_config() -> dict:
    openapi_url = os.getenv("OPENAPI_URL")
    if not openapi_url:
        raise ValueError("OPENAPI_URL environment variable is required")
    
    return {
        "openapi_url": openapi_url,
        "refresh_interval": int(os.getenv("REFRESH_INTERVAL", "300")),
        "base_url": os.getenv("BASE_URL", "")
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
    
    loader = OpenAPILoader(config["openapi_url"])
    loader.load()  # Try to load, but don't fail if it doesn't work
    
    base_url = extract_base_url(config["openapi_url"], loader.base_url, config["base_url"])
    
    var_manager = VariableManager()
    executor = RequestExecutor(var_manager, base_url)
    
    server = Server("openapi-mcp")
    register_tools(server, loader, executor, var_manager)
    
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
