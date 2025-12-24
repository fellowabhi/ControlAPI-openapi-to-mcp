#!/bin/bash
# Auto-download and run ControlAPI-MCP from GitHub releases

REPO="fellowabhi/ControlAPI-openapi-to-mcp"
BINARY_NAME="controlapi-mcp"
INSTALL_DIR="${HOME}/.local/bin/controlapi-mcp"
BINARY_PATH="${INSTALL_DIR}/${BINARY_NAME}"

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Function to get latest release download URL
get_latest_release_url() {
    curl -s "https://api.github.com/repos/${REPO}/releases/latest" \
        | grep "browser_download_url.*${BINARY_NAME}" \
        | cut -d '"' -f 4
}

# Check if binary exists and is executable
if [ ! -f "$BINARY_PATH" ] || [ ! -x "$BINARY_PATH" ]; then
    echo "📥 Downloading ControlAPI-MCP binary from latest release..."
    
    DOWNLOAD_URL=$(get_latest_release_url)
    
    if [ -z "$DOWNLOAD_URL" ]; then
        echo "❌ Error: Could not find release download URL"
        echo "Please check: https://github.com/${REPO}/releases"
        exit 1
    fi
    
    # Download the binary
    if curl -L -o "$BINARY_PATH" "$DOWNLOAD_URL"; then
        chmod +x "$BINARY_PATH"
        echo "✅ Downloaded and installed to: $BINARY_PATH"
    else
        echo "❌ Error: Failed to download binary"
        exit 1
    fi
fi

# Run the binary with all environment variables passed through
exec "$BINARY_PATH" "$@"
