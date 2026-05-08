# Platform Test Matrix

Windows:
- Fetch runtime
- Build NSIS installer
- Install on clean VM
- Verify API and dashboard

Linux:
- Build .deb or tarball
- Install on Ubuntu VM
- Verify service startup

macOS:
- Build .app scaffold
- Sign/notarize with Developer ID
- Verify launch

Update:
- Generate SHA256
- Publish manifest
- Verify update artifact
