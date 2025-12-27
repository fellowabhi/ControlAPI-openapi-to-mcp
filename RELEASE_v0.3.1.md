# ControlAPI-MCP v0.3.1 - Critical Bugfix

## 🐛 Critical Bug Fixed

### Query Parameters Not Passed in GET Requests

**Issue:** Query parameters were being stripped from all GET requests, making search, filtering, and pagination completely non-functional.

**Root Cause:** When `httpx.Client().request()` receives both a URL with query parameters AND a `params` argument, it discards the URL query parameters and only uses the params dict. Since the code was passing an empty dict `{}` when no explicit `query_params` were provided, all URL query strings were being stripped.

**Example of broken behavior:**
```python
# User makes request
execute_request(
    method="GET",
    path="/api/v1/service-types/?is_package=true&page_size=3"
)

# Before fix: Query parameters were lost
# API received: /api/v1/service-types/ (no parameters!)

# After fix: Query parameters work correctly
# API receives: /api/v1/service-types/?is_package=true&page_size=3 ✅
```

**Fix:** 
- Extract query parameters from URL path if present
- Merge with explicit `query_params` argument (explicit params take precedence)
- Only pass `params` to httpx if non-empty

## 📋 Test Cases (All Now Pass)

✅ **Boolean filter**: `?is_package=true` - Returns only packages  
✅ **Pagination**: `?page_size=5` - Returns 5 items  
✅ **Search**: `?search=brake` - Returns filtered results  
✅ **Combined**: `?category=diagnostics&search=battery&page_size=2` - All params work together  
✅ **Mixed approach**: Both URL params and explicit `query_params` dict merge correctly

## 🔧 Technical Details

**File changed:** `src/request_executor.py`

**Changes:**
1. Import `urllib.parse` for query string handling
2. Extract and parse query parameters from path using `parse_qs()`
3. Merge URL params with explicit `query_params` dict
4. Strip query string from path before URL construction
5. Pass `None` instead of `{}` to httpx when no params

## 💥 Impact

This bug affected:
- ❌ All GET endpoints with query parameters
- ❌ Filtering and search functionality  
- ❌ Pagination controls
- ❌ Any endpoint relying on query strings

**Now fixed:** All query parameter functionality fully restored.

## 🙏 Thanks

Thanks to the detailed bug report with curl comparisons and debugger traces that made this easy to diagnose!
