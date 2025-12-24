#!/bin/bash
# Auto-download and run ControlAPI-MCP from GitHub releases

REPO="fellowabhi/ControlAPI-openapi-to-mcp"
BINARY_NAME="controlapi-mcp"
INSTALL_DIR="${HOME}/.local/bin/controlapi-mcp"
BINARY_PATH="${INSTALL_DIR}/${BINARY_NAME}"
VERSION_FILE="${INSTALL_DIR}/.version"

# Create install directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Function to get latest release version
get_latest_version() {
    curl -s "https://api.github.com/repos/${REPO}/releases/latest" \
        | grep '"tag_name":' \
        | cut -d '"' -f 4
}

# Function to get latest release download URL
get_latest_release_url() {
    curl -s "https://api.github.com/repos/${REPO}/releases/latest" \
        | grep "browser_download_url.*${BINARY_NAME}" \
        | cut -d '"' -f 4
}

# Get latest version from GitHub
LATEST_VERSION=$(get_latest_version)

# Get local version if exists
LOCAL_VERSION=""
if [ -f "$VERSION_FILE" ]; then
    LOCAL_VERSION=$(cat "$VERSION_FILE")
fi

# Check if we need to download (no binary, no version file, or newer version available)
NEEDS_DOWNLOAD=false

if [ ! -f "$BINARY_PATH" ] || [ ! -x "$BINARY_PATH" ]; then
    NEEDS_DOWNLOAD=true
    echo "📥 Binary not found. Downloading ControlAPI-MCP..."
elif [ "$LOCAL_VERSION" != "$LATEST_VERSION" ]; then
    NEEDS_DOWNLOAD=true
    echo "🔄 New version available: $LATEST_VERSION (current: $LOCAL_VERSION)"
    echo "📥 Downloading update..."
fi

if [ "$NEEDS_DOWNLOAD" = true ]; then
    DOWNLOAD_URL=$(get_latest_release_url)
    
    if [ -z "$DOWNLOAD_URL" ]; then
        echo "❌ Error: Could not find release download URL"
        echo "Please check: https://github.com/${REPO}/releases"
        exit 1
    fi
    
    # Download the binary
    if curl -L -o "$BINARY_PATH" "$DOWNLOAD_URL"; then
        chmod +x "$BINARY_PATH"
        echo "$LATEST_VERSION" > "$VERSION_FILE"
        echo "✅ Downloaded and installed version $LATEST_VERSION"
        echo "📍 Location: $BINARY_PATH"
    else
        echo "❌ Error: Failed to download binary"
        exit 1
    fi
fi

# Run the binary with all environment variables passed through
exec "$BINARY_PATH" "$@"
