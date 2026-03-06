import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socket


class DebugHandler(BaseHTTPRequestHandler):
    request_history = []
    var_manager = None
    context_manager = None
    
    def log_message(self, format, *args):
        pass  # Suppress server logs
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        
        elif parsed.path == '/api/history':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(self.request_history[-50:]).encode())
        
        elif parsed.path == '/api/variables':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            vars_data = self.var_manager.get_all() if self.var_manager else {}
            self.wfile.write(json.dumps(vars_data).encode())
        
        elif parsed.path == '/api/server':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            server_data = self.context_manager.get_info() if self.context_manager else {}
            self.wfile.write(json.dumps(server_data).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_html(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <title>ControlAPI MCP Debug</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #1e1e1e; color: #d4d4d4; }
        .header { background: #252526; padding: 15px 20px; border-bottom: 1px solid #3c3c3c; }
        .header h1 { font-size: 16px; font-weight: 500; }
        .server-info { background: #2d2d30; padding: 10px 20px; font-size: 12px; border-bottom: 1px solid #3c3c3c; }
        .server-info span { margin-right: 20px; }
        .container { display: flex; height: calc(100vh - 90px); }
        .sidebar { width: 250px; background: #252526; border-right: 1px solid #3c3c3c; overflow-y: auto; }
        .main { flex: 1; overflow-y: auto; padding: 20px; }
        .tab { padding: 10px 15px; cursor: pointer; border-left: 3px solid transparent; font-size: 13px; }
        .tab:hover { background: #2a2d2e; }
        .tab.active { background: #37373d; border-left-color: #007acc; }
        .req-item { background: #2d2d30; margin-bottom: 10px; border-radius: 4px; overflow: hidden; border: 1px solid #3c3c3c; }
        .req-header { padding: 12px 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
        .req-header:hover { background: #37373d; }
        .method { padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: 600; margin-right: 10px; }
        .method.GET { background: #4caf50; color: white; }
        .method.POST { background: #2196f3; color: white; }
        .method.PATCH { background: #ff9800; color: white; }
        .method.DELETE { background: #f44336; color: white; }
        .status { font-size: 11px; padding: 2px 8px; border-radius: 3px; }
        .status.ok { background: #4caf50; color: white; }
        .status.error { background: #f44336; color: white; }
        .req-body { padding: 0; background: #1e1e1e; border-top: 1px solid #3c3c3c; display: none; }
        .req-body.show { display: block; }
        .section { margin: 15px; }
        .section-header { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #2d2d30; border: 1px solid #3c3c3c; border-radius: 4px; cursor: pointer; margin-bottom: 5px; }
        .section-header:hover { background: #37373d; }
        .section-title { font-size: 12px; font-weight: 600; color: #d4d4d4; }
        .section-toggle { font-size: 10px; color: #858585; user-select: none; }
        .section-content { display: none; padding: 10px; background: #1e1e1e; border: 1px solid #3c3c3c; border-radius: 4px; margin-bottom: 10px; }
        .section-content.show { display: block; }
        .json-container { background: #1e1e1e; padding: 10px; border-radius: 4px; overflow-x: auto; font-family: "Courier New", monospace; font-size: 12px; line-height: 1.5; white-space: pre-wrap; word-wrap: break-word; }
        .json-key { color: #9cdcfe; }
        .json-string { color: #ce9178; }
        .json-number { color: #b5cea8; }
        .json-boolean { color: #569cd6; }
        .json-null { color: #569cd6; }
        .json-bracket { color: #d4d4d4; }
        .var-item { background: #2d2d30; padding: 12px 15px; margin-bottom: 8px; border-radius: 4px; border: 1px solid #3c3c3c; }
        .var-key { color: #9cdcfe; font-weight: 600; margin-bottom: 5px; font-size: 13px; }
        .var-value { color: #ce9178; font-size: 12px; word-break: break-all; }
        .empty { text-align: center; padding: 40px; color: #6e6e6e; font-size: 14px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: #2d2d30; padding: 15px; border-radius: 4px; border: 1px solid #3c3c3c; }
        .stat-label { font-size: 11px; color: #858585; margin-bottom: 5px; }
        .stat-value { font-size: 20px; font-weight: 600; }
    </style>
</head>
<body>
    <div class="header">
        <h1>&#128269; ControlAPI MCP Debug Console</h1>
    </div>
    <div class="server-info">
        <span id="serverName">Server: -</span>
        <span id="serverUrl">URL: -</span>
        <span id="endpoints">Endpoints: 0</span>
    </div>
    <div class="container">
        <div class="sidebar">
            <div class="tab active" onclick="showTab('requests')">&#128225; Requests</div>
            <div class="tab" onclick="showTab('variables')">&#128274; Variables</div>
        </div>
        <div class="main">
            <div id="requests-view">
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-label">TOTAL REQUESTS</div>
                        <div class="stat-value" id="totalReqs">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">SUCCESS</div>
                        <div class="stat-value" style="color: #4caf50" id="successReqs">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">ERRORS</div>
                        <div class="stat-value" style="color: #f44336" id="errorReqs">0</div>
                    </div>
                </div>
                <div id="requestList"></div>
            </div>
            <div id="variables-view" style="display:none;">
                <div id="variableList"></div>
            </div>
        </div>
    </div>
    <script>
        let lastReqCount = 0;
        
        // Get relative time
        function getRelativeTime(timestamp) {
            const seconds = Math.floor((Date.now() - timestamp * 1000) / 1000);
            if (seconds < 60) return seconds + ' sec ago';
            const minutes = Math.floor(seconds / 60);
            if (minutes < 60) return minutes + ' min ago';
            const hours = Math.floor(minutes / 60);
            if (hours < 24) return hours + ' hr ago';
            const days = Math.floor(hours / 24);
            return days + ' day' + (days > 1 ? 's' : '') + ' ago';
        }
        
        // Check if JSON is empty
        function isEmptyJson(obj) {
            if (!obj) return true;
            if (typeof obj === 'string') {
                try { obj = JSON.parse(obj); } catch(e) { return false; }
            }
            if (typeof obj === 'object') {
                return Object.keys(obj).length === 0;
            }
            return false;
        }
        
        // Syntax highlight JSON
        function syntaxHighlight(json) {
            if (typeof json !== 'string') {
                json = JSON.stringify(json, null, 2);
            }
            json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
                let cls = 'json-number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'json-key';
                    } else {
                        cls = 'json-string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'json-boolean';
                } else if (/null/.test(match)) {
                    cls = 'json-null';
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
        }
        
        function showTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('requests-view').style.display = tab === 'requests' ? 'block' : 'none';
            document.getElementById('variables-view').style.display = tab === 'variables' ? 'block' : 'none';
        }
        
        function toggleReq(id) {
            document.getElementById('body-' + id).classList.toggle('show');
        }
        
        function toggleSection(event, sectionId) {
            event.stopPropagation();
            const content = document.getElementById(sectionId);
            const toggle = event.currentTarget.querySelector('.section-toggle');
            content.classList.toggle('show');
            toggle.textContent = content.classList.contains('show') ? '▼' : '▶';
        }
        
        async function refresh() {
            try {
                const [history, vars, server] = await Promise.all([
                    fetch('/api/history').then(r => r.json()),
                    fetch('/api/variables').then(r => r.json()),
                    fetch('/api/server').then(r => r.json())
                ]);
                
                // Update server info (no DOM rebuild)
                document.getElementById('serverName').textContent = 'Server: ' + (server.nickname || '-');
                document.getElementById('serverUrl').textContent = 'URL: ' + (server.openapi_url || '-');
                document.getElementById('endpoints').textContent = 'Endpoints: ' + (server.endpoint_count || 0);
                
                // Update stats (no DOM rebuild)
                const total = history.length;
                const success = history.filter(r => r.status >= 200 && r.status < 300).length;
                const errors = history.filter(r => r.status >= 400 || r.status === 0).length;
                
                document.getElementById('totalReqs').textContent = total;
                document.getElementById('successReqs').textContent = success;
                document.getElementById('errorReqs').textContent = errors;
                
                // Update requests or timestamps
                const reqList = document.getElementById('requestList');
                if (history.length !== lastReqCount) {
                    if (history.length === 0) {
                        reqList.innerHTML = '<div class="empty">No requests yet</div>';
                    } else {
                        // Reverse once for display (newest first)
                        const reversed = history.slice().reverse();
                        reqList.innerHTML = reversed.map((req, i) => {
                            // Use actual index from original array
                            const actualIndex = history.length - 1 - i;
                            const isLatest = i === 0;
                            return `
                            <div class="req-item">
                                <div class="req-header" onclick="toggleReq(${actualIndex})">
                                    <div>
                                        <span class="method ${req.method}">${req.method}</span>
                                        <span>${req.path}</span>
                                        <div style="font-size: 10px; color: #858585; margin-top: 3px;" class="req-timestamp" data-timestamp="${req.timestamp}">${getRelativeTime(req.timestamp)}</div>
                                    </div>
                                    <div>
                                        <span class="status ${req.status >= 200 && req.status < 300 ? 'ok' : 'error'}">${req.status}</span>
                                        <span style="margin-left: 10px; font-size: 11px; color: #858585">${req.elapsed_ms}ms</span>
                                    </div>
                                </div>
                                <div class="req-body${isLatest ? ' show' : ''}" id="body-${actualIndex}">
                                    ${!isEmptyJson(req.request_body) ? `
                                    <div class="section">
                                        <div class="section-header" onclick="toggleSection(event, 'req-body-${actualIndex}')">
                                            <span class="section-title">Request Body</span>
                                            <span class="section-toggle">${isLatest ? '▼' : '▶'}</span>
                                        </div>
                                        <div class="section-content${isLatest ? ' show' : ''}" id="req-body-${actualIndex}">
                                            <div class="json-container">${syntaxHighlight(req.request_body)}</div>
                                        </div>
                                    </div>` : ''}
                                    ${!isEmptyJson(req.request_params) ? `
                                    <div class="section">
                                        <div class="section-header" onclick="toggleSection(event, 'req-params-${actualIndex}')">
                                            <span class="section-title">Request Params</span>
                                            <span class="section-toggle">${isLatest ? '▼' : '▶'}</span>
                                        </div>
                                        <div class="section-content${isLatest ? ' show' : ''}" id="req-params-${actualIndex}">
                                            <div class="json-container">${syntaxHighlight(req.request_params)}</div>
                                        </div>
                                    </div>` : ''}
                                    ${!isEmptyJson(req.request_headers) ? `
                                    <div class="section">
                                        <div class="section-header" onclick="toggleSection(event, 'req-headers-${actualIndex}')">
                                            <span class="section-title">Request Headers</span>
                                            <span class="section-toggle">${isLatest ? '▼' : '▶'}</span>
                                        </div>
                                        <div class="section-content${isLatest ? ' show' : ''}" id="req-headers-${actualIndex}">
                                            <div class="json-container">${syntaxHighlight(req.request_headers)}</div>
                                        </div>
                                    </div>` : ''}
                                    <div class="section">
                                        <div class="section-header" onclick="toggleSection(event, 'response-${actualIndex}')">
                                            <span class="section-title">Response</span>
                                            <span class="section-toggle">${isLatest ? '▼' : '▶'}</span>
                                        </div>
                                        <div class="section-content${isLatest ? ' show' : ''}" id="response-${actualIndex}">
                                            <div class="json-container">${syntaxHighlight(req.response_body)}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `}).join('');
                    }
                    lastReqCount = history.length;
                } else {
                    // Update timestamps only
                    document.querySelectorAll('.req-timestamp').forEach(el => {
                        const timestamp = parseFloat(el.dataset.timestamp);
                        el.textContent = getRelativeTime(timestamp);
                    });
                }
                
                // Update variables
                const varList = document.getElementById('variableList');
                const varKeys = Object.keys(vars);
                if (varKeys.length === 0) {
                    varList.innerHTML = '<div class="empty">No variables stored</div>';
                } else {
                    varList.innerHTML = varKeys.map(key => `
                        <div class="var-item">
                            <div class="var-key">${key}</div>
                            <div class="var-value">${vars[key].length > 100 ? vars[key].substring(0, 100) + '...' : vars[key]}</div>
                        </div>
                    `).join('');
                }
            } catch (err) {
                console.error('Refresh failed:', err);
            }
        }
        
        refresh();
        setInterval(refresh, 2000);
    </script>
</body>
</html>'''


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


class DebugServer:
    DEFAULT_PORT = 45133  # Unlikely to conflict with common applications
    
    def __init__(self, var_manager, context_manager, custom_port=None):
        self.port = custom_port or self.DEFAULT_PORT
        DebugHandler.var_manager = var_manager
        DebugHandler.context_manager = context_manager
        self.server = None
        self.thread = None
        self.failed = False
        self.error_message = None
    
    def start(self):
        ports_to_try = [self.port, 0]  # 0 = let OS pick a free port
        for port in ports_to_try:
            try:
                self.server = HTTPServer(('0.0.0.0', port), DebugHandler)
                actual_port = self.server.server_address[1]
                self.port = actual_port
                self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                self.thread.start()
                return actual_port
            except OSError:
                continue
        self.failed = True
        self.error_message = "Could not bind to any port for debug monitor"
        return None
    
    @staticmethod
    def log_request(method, path, status, elapsed_ms, request_body, request_headers, request_params, response_body):
        import time
        DebugHandler.request_history.append({
            'method': method,
            'path': path,
            'status': status,
            'elapsed_ms': elapsed_ms,
            'request_body': request_body,
            'request_headers': request_headers,
            'request_params': request_params,
            'response_body': response_body,
            'timestamp': time.time(),
        })

    @staticmethod
    def get_last_response() -> dict | None:
        """Get the most recent request+response from history."""
        if DebugHandler.request_history:
            return DebugHandler.request_history[-1]
        return None

    @staticmethod
    def get_response(index: int = -1) -> dict | None:
        """Get a specific request+response from history by index."""
        try:
            return DebugHandler.request_history[index]
        except (IndexError, TypeError):
            return None

    @staticmethod
    def get_history_count() -> int:
        """Get the total number of stored requests."""
        return len(DebugHandler.request_history)
