"""
Shared output utilities for token-efficient tool responses.

Provides pagination, field filtering, JSONPath extraction, body truncation,
and compact JSON formatting. Used by all MCP tools to minimize token usage
while keeping full data available on demand.
"""

import json
from typing import Any, Optional


def compact_json(data: Any) -> str:
    """JSON with no whitespace — saves ~30-40% tokens vs indent=2."""
    return json.dumps(data, separators=(',', ':'))


def pretty_json(data: Any) -> str:
    """Standard indented JSON for when readability is preferred."""
    return json.dumps(data, indent=2)


def paginate(items: list, limit: int = 10, offset: int = 0) -> dict:
    """
    Paginate a list of items.

    Returns:
        {"results": [...], "total": N, "limit": L, "offset": O, "has_more": bool}
    """
    total = len(items)
    sliced = items[offset:offset + limit]
    return {
        "results": sliced,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }


def filter_fields(data: Any, fields: list[str]) -> Any:
    """
    Keep only specified keys from dicts. Works on a single dict or list of dicts.
    Returns data unchanged if fields is empty/None.
    """
    if not fields:
        return data

    if isinstance(data, dict):
        return {k: v for k, v in data.items() if k in fields}

    if isinstance(data, list):
        return [
            {k: v for k, v in item.items() if k in fields}
            if isinstance(item, dict) else item
            for item in data
        ]

    return data


def truncate_body(body: Any, max_length: int) -> Any:
    """
    Truncate response body to max_length characters.
    Works on strings or JSON-serializable objects.
    Returns original if under limit.
    """
    if body is None:
        return None
    
    if isinstance(body, str):
        if len(body) <= max_length:
            return body
        return body[:max_length] + "...[truncated]"
    
    # For dicts/lists, serialize then truncate
    serialized = json.dumps(body, separators=(',', ':'))
    if len(serialized) <= max_length:
        return body
    
    return serialized[:max_length] + "...[truncated]"


def apply_jsonpath(data: Any, expression: str) -> Any:
    """
    Apply a JSONPath expression to extract specific values from data.
    
    Args:
        data: dict or list to query
        expression: JSONPath expression (e.g., "$.results[0].name", "$.items[*].id")
    
    Returns:
        Extracted value(s). Single value if one match, list if multiple.
    """
    try:
        from jsonpath_ng import parse as jsonpath_parse
        
        parsed = jsonpath_parse(expression)
        matches = parsed.find(data)
        
        if not matches:
            return {"jsonpath_error": f"No matches for '{expression}'", "available_keys": list(data.keys()) if isinstance(data, dict) else None}
        
        values = [m.value for m in matches]
        
        # Return single value if only one match
        if len(values) == 1:
            return values[0]
        return values
        
    except Exception as e:
        return {"jsonpath_error": str(e)}


def format_endpoint_compact(endpoint: dict) -> str:
    """
    Format an endpoint as a compact one-liner.
    e.g., "POST /api/v1/orders/ [json,form] - Create an order"
    """
    method = endpoint.get("method", "?")
    path = endpoint.get("path", "?")
    summary = endpoint.get("summary", "")
    content_types = endpoint.get("content_types", [])
    
    parts = [f"{method} {path}"]
    
    if content_types:
        # Shorten content type names
        short_types = []
        for ct in content_types:
            if "json" in ct:
                short_types.append("json")
            elif "form-urlencoded" in ct:
                short_types.append("form")
            elif "multipart" in ct:
                short_types.append("multipart")
            else:
                short_types.append(ct.split("/")[-1])
        parts.append(f"[{','.join(short_types)}]")
    
    if summary:
        parts.append(f"- {summary}")
    
    return " ".join(parts)


def format_schema_compact(schema: dict) -> str:
    """
    Flatten an OpenAPI schema into compact 'field: type' lines.
    Handles nested objects and arrays.
    """
    lines = []
    _flatten_schema(schema, lines, indent=0)
    return "\n".join(lines)


def _flatten_schema(schema: dict, lines: list, indent: int = 0, prefix: str = ""):
    """Recursively flatten a JSON schema into readable lines."""
    if not isinstance(schema, dict):
        return
    
    schema_type = schema.get("type", "object")
    required_fields = set(schema.get("required", []))
    properties = schema.get("properties", {})
    
    # Handle allOf, oneOf, anyOf
    for combiner in ("allOf", "oneOf", "anyOf"):
        if combiner in schema:
            for sub_schema in schema[combiner]:
                _flatten_schema(sub_schema, lines, indent, prefix)
            return
    
    # Handle array items
    if schema_type == "array":
        items = schema.get("items", {})
        if items.get("type") == "object" or "properties" in items:
            lines.append(f"{'  ' * indent}{prefix}array of objects:")
            _flatten_schema(items, lines, indent + 1)
        else:
            item_type = items.get("type", "any")
            lines.append(f"{'  ' * indent}{prefix}array of {item_type}")
        return
    
    # Handle object properties
    if properties:
        for field_name, field_schema in properties.items():
            field_type = field_schema.get("type", "any")
            req = " (required)" if field_name in required_fields else ""
            enum_values = field_schema.get("enum")
            
            if field_type == "object" or "properties" in field_schema:
                lines.append(f"{'  ' * indent}{field_name}: object{req}")
                _flatten_schema(field_schema, lines, indent + 1)
            elif field_type == "array":
                items = field_schema.get("items", {})
                if items.get("type") == "object" or "properties" in items:
                    lines.append(f"{'  ' * indent}{field_name}: array of objects{req}")
                    _flatten_schema(items, lines, indent + 1)
                else:
                    item_type = items.get("type", "any")
                    lines.append(f"{'  ' * indent}{field_name}: array of {item_type}{req}")
            elif enum_values:
                lines.append(f"{'  ' * indent}{field_name}: {field_type}{req} enum={enum_values}")
            else:
                # Include format if present (e.g., "string (format: date-time)")
                fmt = field_schema.get("format")
                fmt_str = f" (format: {fmt})" if fmt else ""
                lines.append(f"{'  ' * indent}{field_name}: {field_type}{fmt_str}{req}")
    elif schema_type and schema_type != "object":
        lines.append(f"{'  ' * indent}{prefix}{schema_type}")


def format_response(
    data: Any,
    compact: bool = True,
    fields: Optional[list[str]] = None,
    jsonpath: Optional[str] = None,
    max_body_length: Optional[int] = None,
) -> str:
    """
    Master formatter that chains filtering, JSONPath, truncation, and serialization.
    
    Args:
        data: The data to format
        compact: If True, use compact JSON (no whitespace)
        fields: Optional list of keys to keep
        jsonpath: Optional JSONPath expression to extract specific values
        max_body_length: Optional max character length for the output
    
    Returns:
        Formatted string ready to return to the AI
    """
    result = data
    
    # Apply JSONPath first (most specific filter)
    if jsonpath:
        result = apply_jsonpath(result, jsonpath)
    
    # Apply field filter
    if fields:
        result = filter_fields(result, fields)
    
    # Serialize
    if isinstance(result, str):
        output = result
    else:
        output = compact_json(result) if compact else pretty_json(result)
    
    # Truncate if needed
    if max_body_length and len(output) > max_body_length:
        output = output[:max_body_length] + "...[truncated]"
    
    return output
