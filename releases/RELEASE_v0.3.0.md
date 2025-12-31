# ControlAPI-MCP v0.3.0 - macOS Support

## 🎉 New Features

### macOS Support
- ✅ **Native macOS binaries** - Works on Intel and Apple Silicon Macs
- ✅ **Auto-detection** - `auto-run.sh` automatically downloads the correct binary for your platform
- ✅ **One-click install** - Same seamless experience on both Linux and macOS

### Cross-Platform
- **Linux** - `controlapi-mcp-linux` (x86_64)
- **macOS** - `controlapi-mcp-macos` (universal binary)

## 🔧 Technical Changes

- **GitHub Actions:** Matrix build strategy for parallel Linux + macOS builds
- **auto-run.sh:** OS detection using `uname -s` to download platform-specific binary
- **Release artifacts:** Two separate binaries per release

## 📥 Installation

### macOS & Linux (One-Click)
Click the install link in the README or use:

```bash
curl -O https://raw.githubusercontent.com/fellowabhi/ControlAPI-openapi-to-mcp/main/auto-run.sh
chmod +x auto-run.sh
./auto-run.sh
```

The script automatically detects your OS and downloads the correct binary!

## 🙏 Feedback

Please report any macOS-specific issues on GitHub!
