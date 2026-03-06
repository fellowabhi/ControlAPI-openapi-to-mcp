from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ServerContext:
    """Represents the current server configuration and state."""
    openapi_url: str
    base_url: Optional[str] = None
    nickname: Optional[str] = None
    loaded_at: Optional[datetime] = None
    endpoint_count: int = 0
    last_request_at: Optional[datetime] = None
    last_request_method: Optional[str] = None
    last_request_path: Optional[str] = None
    load_error: Optional[str] = None
    is_loaded: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "openapi_url": self.openapi_url,
            "base_url": self.base_url,
            "nickname": self.nickname or "Unnamed Server",
            "loaded_at": self.loaded_at.isoformat() if self.loaded_at else None,
            "endpoint_count": self.endpoint_count,
            "last_request_at": self.last_request_at.isoformat() if self.last_request_at else None,
            "last_request_method": self.last_request_method,
            "last_request_path": self.last_request_path,
            "load_error": self.load_error,
            "is_loaded": self.is_loaded,
        }


class ContextManager:
    """Manages server context and switching history."""
    
    def __init__(self, openapi_url: str, base_url: Optional[str] = None, nickname: Optional[str] = None):
        self.debug_url: Optional[str] = None
        self.current = ServerContext(
            openapi_url=openapi_url,
            base_url=base_url,
            nickname=nickname,
        )
        self.history: list[ServerContext] = []
        self._max_history = 10
        self._pending_first_request = False
    
    def switch_server(self, openapi_url: str, base_url: Optional[str] = None, nickname: Optional[str] = None):
        """Switch to a new server configuration."""
        # Save current to history
        if self.current.openapi_url:
            self.history.insert(0, self.current)
            if len(self.history) > self._max_history:
                self.history = self.history[:self._max_history]
        
        # Create new context
        self.current = ServerContext(
            openapi_url=openapi_url,
            base_url=base_url,
            nickname=nickname,
        )
        self._pending_first_request = True
        self.debug_error: Optional[str] = None
    
    def update_load_status(self, is_loaded: bool, endpoint_count: int = 0, load_error: Optional[str] = None):
        """Update the load status after schema fetch."""
        self.current.is_loaded = is_loaded
        self.current.endpoint_count = endpoint_count
        self.current.load_error = load_error
        if is_loaded:
            self.current.loaded_at = datetime.now()
    
    def record_request(self, method: str, path: str):
        """Record a request execution."""
        self.current.last_request_at = datetime.now()
        self.current.last_request_method = method
        self.current.last_request_path = path
        self._pending_first_request = False
    
    def get_info(self) -> dict:
        """Get current server info."""
        info = self.current.to_dict()
        info["needs_first_request_warning"] = self._pending_first_request
        if self.debug_url:
            info["debug_ui_url"] = self.debug_url
        elif self.debug_error:
            info["debug_ui_error"] = self.debug_error
        return info
    
    def get_history(self) -> list[dict]:
        """Get server switching history."""
        return [ctx.to_dict() for ctx in self.history]
    
    def should_warn_first_request(self) -> bool:
        """Check if we should warn about first request after switch."""
        return self._pending_first_request
    
    def get_display_name(self) -> str:
        """Get friendly display name for current server."""
        if self.current.nickname:
            return self.current.nickname
        return self.current.openapi_url
