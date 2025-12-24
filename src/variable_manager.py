import re
import json
from typing import Any


class VariableManager:
    def __init__(self):
        self._vars: dict[str, str] = {}

    def set(self, key: str, value: str) -> None:
        self._vars[key] = value

    def get(self, key: str) -> str:
        return self._vars.get(key, "")

    def get_all(self) -> dict[str, str]:
        return dict(self._vars)

    def substitute(self, text: str) -> str:
        def replacer(match):
            key = match.group(1)
            return self._vars.get(key, match.group(0))
        return re.sub(r'\{\{(\w+)\}\}', replacer, text)

    def apply_to_request(self, headers: dict, body: Any, path: str) -> tuple[dict, Any, str]:
        new_headers = {k: self.substitute(v) for k, v in headers.items()}
        new_path = self.substitute(path)
        
        if isinstance(body, str):
            new_body = self.substitute(body)
        elif isinstance(body, dict):
            new_body = json.loads(self.substitute(json.dumps(body)))
        else:
            new_body = body
            
        return new_headers, new_body, new_path
