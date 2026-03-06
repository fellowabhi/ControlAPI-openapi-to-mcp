# How to Release

1. **Bump version** in `pyproject.toml`
2. **Add release notes** at `releases/RELEASE_v{VERSION}.md`
3. **Commit and push**
   ```bash
   git add -A && git commit -m "chore: bump version to vX.Y.Z" && git push
   ```
4. **Tag and push tag** — this triggers GitHub Actions to build Linux/macOS binaries and create the GitHub release automatically
   ```bash
   git tag vX.Y.Z && git push origin vX.Y.Z
   ```

The workflow (`.github/workflows/release.yml`) picks up the tag, builds both binaries, and attaches them to the release using the notes from `releases/RELEASE_v{VERSION}.md`.
