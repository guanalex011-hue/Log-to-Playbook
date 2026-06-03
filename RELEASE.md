# Release Process

Log-to-Playbook uses semantic versioning.

## Version Checklist

1. Update `pyproject.toml`.
2. Update `src/log_to_playbook/__init__.py`.
3. Update `CHANGELOG.md`.
4. Run:

   ```bash
   python -m pytest
   python -m build
   ```

5. Commit the version changes.
6. Create and push a version tag:

   ```bash
   git tag v0.2.0
   git push origin main --tags
   ```

7. The release workflow builds distribution artifacts for the tag.

## Manual GitHub Release

If the automated release workflow is unavailable, create a release manually:

```bash
gh release create v0.2.0 --title "v0.2.0" --notes-file CHANGELOG.md
```
