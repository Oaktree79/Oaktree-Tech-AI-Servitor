# Bundled Python Runtime

Place a portable Python runtime here for true offline one-click installs.

Recommended:
- Windows: python-3.11.x-embed-amd64.zip extracted here as `python/`
- macOS: Python framework or Briefcase bundle
- Linux: AppImage/portable CPython or system Python bootstrap fallback

Expected layout for Windows:

```text
installer/runtime/python/
  python.exe
  python311.zip
  DLLs/
  Lib/
```

The bootstrap scripts detect this runtime first, then fall back to system Python.
