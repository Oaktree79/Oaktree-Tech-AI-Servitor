# One-Click Installer Productization

This build adds:

1. Bundled Python runtime scaffold
2. Auto dependency install
3. Service auto-registration files
4. GUI/browser auto-launch
5. Embedded configuration wizard
6. Automatic environment setup
7. Auto-generated secrets
8. Installer branding/icons
9. Auto-update system
10. Crash reporting

## Windows

```powershell
powershell -ExecutionPolicy Bypass -File installer\windows\install_one_click.ps1
```

To build an NSIS installer:

```powershell
makensis installer\windows\AI-Serviter.nsi
```

## Linux

```bash
bash installer/linux/install_one_click.sh
```

## macOS

Double-click:

```text
installer/macos/install_one_click.command
```

## Bundled runtime

Place portable Python under:

```text
installer/runtime/python/
```

## One-click CLI

```bash
python -m ai_serviter.one_click --root . setup
python -m ai_serviter.one_click --root . launch
```
