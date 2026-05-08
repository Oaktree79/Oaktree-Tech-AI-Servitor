# ISO OS / Installer Media Integration

The uploaded architecture has been integrated as an ISO/VM/installer packaging module.

Important distinction:

- **ISO installer media**: included and supported.
- **Bootable operating system ISO**: scaffold only. A true OS image requires a Linux/Windows live image, bootloader, kernel/initrd, and persistence strategy.
- **Apple iOS**: not applicable. This project is not an Apple iOS app or mobile operating system.

## New files

- `python/ai_serviter/iso_packager.py`
- `python/ai_serviter/gui_app.py`
- `docs/uploaded_complete_solution_architecture.md`
- `docs/ISO_OS_INTEGRATION.md`

## CLI

Create ISO directory tree:

```bash
serviter . create-iso-tree --out AI_SERVITER_ISO --name "AI Serviter"
```

Build ISO if `xorriso`, `genisoimage`, or `mkisofs` exists:

```bash
serviter . build-iso --tree AI_SERVITER_ISO --out AI_SERVITER.iso
```

## GUI

```bash
python -m pip install -e ".[gui]"
serviter-gui
```
