#!/bin/bash
set -e

echo "🔨 Building Control API MCP binary..."

# Create venv if it doesn't exist (for CI environments)
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing dependencies..."
    pip install -e . pyinstaller
fi

# Build using PyInstaller
pyinstaller --clean controlapi-mcp.spec

echo ""
echo "✅ Build complete!"
echo "📦 Binary location: dist/controlapi-mcp"
echo ""
echo "To run the binary:"
echo "  ./dist/controlapi-mcp"
