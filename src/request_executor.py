from dataclasses import dataclass
from typing import Any, Optional
import time
import httpx

from variable_manager import VariableManager


@dataclass
class Response:
    status_code: int
    headers: dict
    body: Any
    elapsed_ms: float


class RequestExecutor:
    def __init__(self, variable_manager: VariableManager, base_url: str):
        self.var_manager = variable_manager
        self.base_url = base_url.rstrip("/")

    def execute(
        self,
        path: str,
        method: str,
        headers: Optional[dict] = None,
        query_params: Optional[dict] = None,
        path_params: Optional[dict] = None,
        body: Any = None,
    ) -> Response:
        headers = headers or {}
        query_params = query_params or {}
        path_params = path_params or {}

        # Apply path params
        for key, value in path_params.items():
            path = path.replace(f"{{{key}}}", str(value))

        # Apply variable substitution
        headers, body, path = self.var_manager.apply_to_request(headers, body, path)

        url = f"{self.base_url}{path}"
        
        start = time.perf_counter()
        try:
            with httpx.Client() as client:
                resp = client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=query_params,
                    json=body if body else None,
                )
            elapsed = (time.perf_counter() - start) * 1000

            try:
                resp_body = resp.json()
            except Exception:
                resp_body = resp.text

            return Response(
                status_code=resp.status_code,
                headers=dict(resp.headers),
                body=resp_body,
                elapsed_ms=round(elapsed, 2),
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return Response(
                status_code=0,
                headers={},
                body={"error": str(e), "type": type(e).__name__},
                elapsed_ms=round(elapsed, 2),
            )
