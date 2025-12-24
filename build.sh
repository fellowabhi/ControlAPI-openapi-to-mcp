#!/bin/bash
set -e

echo "🔨 Building Control API MCP binary..."

# Activate virtual environment
source .venv/bin/activate

# Build using PyInstaller
pyinstaller --clean controlapi-mcp.spec

echo ""
echo "✅ Build complete!"
echo "📦 Binary location: dist/controlapi-mcp"
echo ""
echo "To run the binary:"
echo "  export OPENAPI_URL='http://your-api.com/openapi.json'"
echo "  export BASE_URL='http://your-api.com'  # optional"
echo "  ./dist/controlapi-mcp"
