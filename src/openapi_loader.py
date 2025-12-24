from dataclasses import dataclass, field
from typing import List, Optional
import httpx


@dataclass
class Endpoint:
    path: str
    method: str
    summary: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: dict = field(default_factory=dict)
    request_body: dict = field(default_factory=dict)
    responses: dict = field(default_factory=dict)


class OpenAPILoader:
    def __init__(self, url: str):
        self.url = url
        self.spec: dict = {}
        self.base_url: str = ""
        self.loaded: bool = False
        self.load_error: str = ""

    def load(self) -> dict:
        try:
            resp = httpx.get(self.url)
            resp.raise_for_status()
            self.spec = resp.json()
            servers = self.spec.get("servers", [])
            self.base_url = servers[0]["url"] if servers else ""
            self.loaded = True
            self.load_error = ""
            return self.spec
        except Exception as e:
            self.loaded = False
            self.load_error = f"Failed to load OpenAPI schema: {str(e)}"
            return {}

    def reload(self) -> dict:
        return self.load()

    def get_endpoints(self) -> List[Endpoint]:
        endpoints = []
        paths = self.spec.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ("get", "post", "put", "patch", "delete"):
                    endpoints.append(self._parse_endpoint(path, method, details))
        return endpoints

    def _parse_endpoint(self, path: str, method: str, details: dict) -> Endpoint:
        return Endpoint(
            path=path,
            method=method.upper(),
            summary=details.get("summary", ""),
            description=details.get("description", ""),
            tags=details.get("tags", []),
            parameters=details.get("parameters", []),
            request_body=details.get("requestBody", {}),
            responses=details.get("responses", {}),
        )

    def get_endpoint_schema(self, path: str, method: str) -> Optional[dict]:
        paths = self.spec.get("paths", {})
        if path in paths and method.lower() in paths[path]:
            return paths[path][method.lower()]
        return None

    def search_endpoints(self, query: str) -> List[Endpoint]:
        query = query.lower()
        results = []
        for ep in self.get_endpoints():
            if (query in ep.path.lower() or 
                query in ep.summary.lower() or 
                query in ep.description.lower() or
                any(query in t.lower() for t in ep.tags)):
                results.append(ep)
        return results
