# ControlAPI-MCP v0.2.1 - Hotfix Release

## 🐛 Bug Fixes

### Fixed Zero-Config Startup
- **Critical Fix:** Binary now properly supports zero-config startup (OPENAPI_URL optional)
- Fixed build script for CI environments - auto-creates venv
- Auto-run.sh now includes version checking and auto-updates

## 📋 Changes Since v0.2.0

### Fixed
- Binary compiled with updated code that makes OPENAPI_URL optional
- Build script now works correctly in GitHub Actions CI environment
- Version file tracking in auto-run.sh for automatic updates

### Improved
- Auto-run.sh detects new versions and auto-downloads updates
- Better CI/CD workflow reliability

## 🚀 Installation

**One-Click Install (No Config Needed):**
- [Install in VS Code](https://vscode.dev/redirect/mcp/install?name=controlapi-mcp&config=%7B%22type%22%3A%22stdio%22%2C%22command%22%3A%22bash%22%2C%22args%22%3A%5B%22-c%22%2C%22mkdir%20-p%20~/.local/bin/controlapi-mcp%20%26%26%20curl%20-fsSL%20https%3A//raw.githubusercontent.com/fellowabhi/ControlAPI-openapi-to-mcp/main/auto-run.sh%20-o%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20chmod%20%2Bx%20~/.local/bin/controlapi-mcp/auto-run.sh%20%26%26%20~/.local/bin/controlapi-mcp/auto-run.sh%22%5D%7D)

**Existing Users:**
- auto-run.sh will automatically detect and download v0.2.1 on next run
- Or manually delete `~/.local/bin/controlapi-mcp/.version` to force update

## 📝 Notes

This is a hotfix release to ensure v0.2.0 features work correctly in the binary distribution. All features from v0.2.0 are included and now fully functional:

- ✅ Zero-config startup (no OPENAPI_URL required)
- ✅ Dynamic server switching
- ✅ AI-guided setup workflow
- ✅ 4 new server management tools
- ✅ Server context tracking
- ✅ Auto-update capability

---

**Full Changelog:** https://github.com/fellowabhi/ControlAPI-openapi-to-mcp/compare/v0.2.0...v0.2.1
