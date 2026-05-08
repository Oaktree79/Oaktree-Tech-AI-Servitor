AI Serviter ISO Package
======================

This media contains the AI Serviter autonomous framework, installer scripts,
deployment files, and VM packaging scaffold.

Windows:
  Run setup.bat.

Linux/macOS:
  Run scripts/install_unix.sh.

API:
  serviter-service --root app/python --mode api --host 127.0.0.1 --port 8765

Rufus:
  Rufus can write this ISO as installer media. This is not a complete bootable
  operating system ISO unless you add a bootloader and live OS image.

VM:
  See vm/README_VM.txt.
