from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List
import json
import os
import shutil
import subprocess
import textwrap
import time


@dataclass
class PackagingResult:
    ok: bool
    artifact: str | None
    messages: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class ISOPackager:
    """
    ISO/VM/installer packaging module for AI Serviter.

    This creates an ISO directory tree and can build a Rufus-readable ISO when
    xorriso, genisoimage, or mkisofs is installed.

    Note:
    - This is installer-media packaging, not Apple iOS.
    - A truly bootable OS ISO needs a bootloader and OS image. This module creates
      a portable installer/data ISO scaffold, plus optional VM metadata.
    """

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root).resolve()

    def create_iso_tree(self, output_dir: str | Path, app_name: str = "AI Serviter") -> Path:
        output = Path(output_dir).resolve()
        if output.exists():
            shutil.rmtree(output)
        output.mkdir(parents=True)

        for folder in ["app", "installer", "vm", "scripts", "docs"]:
            (output / folder).mkdir(parents=True, exist_ok=True)

        # Copy Python package and deployment files
        src_python = self.project_root / "python"
        if src_python.exists():
            shutil.copytree(src_python, output / "app" / "python", dirs_exist_ok=True)

        for optional in ["deploy", "scripts", "README.md", "LICENSE"]:
            src = self.project_root / optional
            dst = output / ("docs" if src.is_file() else optional) / src.name if src.is_file() else output / optional
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)

        self.write_autorun(output, app_name)
        self.write_setup_bat(output, app_name)
        self.write_linux_macos_installer(output)
        self.write_windows_nsis(output, app_name)
        self.write_vm_ovf(output, app_name)
        self.write_readme(output, app_name)

        manifest = {
            "app_name": app_name,
            "created_at": time.time(),
            "contents": sorted(str(p.relative_to(output)) for p in output.rglob("*") if p.is_file())[:5000],
        }
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        return output

    def build_iso(self, iso_tree: str | Path, iso_path: str | Path, volume_label: str = "AI_SERVITER") -> PackagingResult:
        iso_tree = Path(iso_tree).resolve()
        iso_path = Path(iso_path).resolve()
        messages: List[str] = []

        tools = [
            ("xorriso", ["xorriso", "-as", "mkisofs", "-o", str(iso_path), "-V", volume_label, "-J", "-r", str(iso_tree)]),
            ("genisoimage", ["genisoimage", "-o", str(iso_path), "-V", volume_label, "-J", "-r", str(iso_tree)]),
            ("mkisofs", ["mkisofs", "-o", str(iso_path), "-V", volume_label, "-J", "-r", str(iso_tree)]),
        ]

        for tool, cmd in tools:
            if shutil.which(tool):
                proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
                messages.append(proc.stdout)
                messages.append(proc.stderr)
                if proc.returncode == 0:
                    return PackagingResult(True, str(iso_path), messages)
                return PackagingResult(False, None, messages + [f"{tool} failed with code {proc.returncode}"])

        return PackagingResult(
            False,
            None,
            messages + ["No ISO builder found. Install xorriso, genisoimage, or mkisofs."],
        )

    def write_autorun(self, output: Path, app_name: str):
        (output / "autorun.inf").write_text(textwrap.dedent(f"""
        [autorun]
        label={app_name}
        open=setup.bat
        icon=setup.bat,0
        """).strip() + "\n", encoding="utf-8")

    def write_setup_bat(self, output: Path, app_name: str):
        (output / "setup.bat").write_text(textwrap.dedent(f"""
        @echo off
        echo {app_name} Setup
        echo ----------------------------------
        echo.
        echo 1. Install Python package locally
        echo 2. Run API server
        echo 3. View VM import instructions
        echo 4. Exit
        echo.
        set /p choice="Enter your choice: "

        if "%choice%"=="1" (
            cd app\\python
            python -m pip install -e ".[dev]"
            pause
        ) else if "%choice%"=="2" (
            cd app\\python
            serviter-service --root . --mode api --host 127.0.0.1 --port 8765
        ) else if "%choice%"=="3" (
            type vm\\README_VM.txt
            pause
        ) else (
            exit
        )
        """).strip() + "\n", encoding="utf-8")

    def write_linux_macos_installer(self, output: Path):
        path = output / "scripts" / "install_unix.sh"
        path.write_text(textwrap.dedent("""
        #!/usr/bin/env bash
        set -euo pipefail
        cd "$(dirname "$0")/../app/python"
        python3 -m venv .venv
        . .venv/bin/activate
        python -m pip install -U pip
        python -m pip install -e ".[dev]"
        echo "Installed. Run: serviter-service --root . --mode api"
        """).strip() + "\n", encoding="utf-8")
        path.chmod(0o755)

    def write_windows_nsis(self, output: Path, app_name: str):
        (output / "installer" / "installer.nsi").write_text(textwrap.dedent(f"""
        !include "MUI2.nsh"

        Name "{app_name}"
        OutFile "AIServiter_Installer.exe"
        InstallDir "$PROGRAMFILES\\AIServiter"
        RequestExecutionLevel admin

        !insertmacro MUI_PAGE_WELCOME
        !insertmacro MUI_PAGE_DIRECTORY
        !insertmacro MUI_PAGE_INSTFILES
        !insertmacro MUI_PAGE_FINISH
        !insertmacro MUI_UNPAGE_WELCOME
        !insertmacro MUI_UNPAGE_CONFIRM
        !insertmacro MUI_UNPAGE_INSTFILES
        !insertmacro MUI_UNPAGE_FINISH
        !insertmacro MUI_LANGUAGE "English"

        Section "Application"
            SetOutPath $INSTDIR
            File /r "..\\app\\python\\*"
            CreateShortCut "$DESKTOP\\AI Serviter.lnk" "$INSTDIR\\run_api.bat"
            FileOpen $0 "$INSTDIR\\run_api.bat" w
            FileWrite $0 "@echo off$\\r$\\n"
            FileWrite $0 "python -m pip install -e .[dev]$\\r$\\n"
            FileWrite $0 "serviter-service --root . --mode api --host 127.0.0.1 --port 8765$\\r$\\n"
            FileClose $0
            WriteUninstaller "$INSTDIR\\Uninstall.exe"
        SectionEnd

        Section "Uninstall"
            Delete "$INSTDIR\\Uninstall.exe"
            Delete "$DESKTOP\\AI Serviter.lnk"
            RMDir /r "$INSTDIR"
        SectionEnd
        """).strip() + "\n", encoding="utf-8")

    def write_vm_ovf(self, output: Path, app_name: str):
        (output / "vm" / "vm_config.ovf").write_text(textwrap.dedent(f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <Envelope xmlns="http://schemas.dmtf.org/ovf/envelope/1"
                  xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1"
                  xmlns:rasd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData"
                  xmlns:vssd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData">
          <References/>
          <DiskSection>
            <Info>Virtual disk information placeholder. Attach your generated VMDK/QCOW2 disk here.</Info>
          </DiskSection>
          <NetworkSection>
            <Info>Logical networks</Info>
            <Network ovf:name="LAN"><Description>Default LAN network</Description></Network>
          </NetworkSection>
          <VirtualSystem ovf:id="AI_SERVITER_VM">
            <Info>AI Serviter virtual machine profile</Info>
            <Name>{app_name}</Name>
            <OperatingSystemSection ovf:id="101">
              <Info>Ubuntu Linux 64-bit recommended</Info>
              <Description>Ubuntu Linux (64-bit)</Description>
            </OperatingSystemSection>
            <VirtualHardwareSection>
              <Info>Virtual hardware requirements</Info>
              <System>
                <vssd:ElementName>Virtual Hardware Family</vssd:ElementName>
                <vssd:InstanceID>0</vssd:InstanceID>
                <vssd:VirtualSystemIdentifier>AI_SERVITER_VM</vssd:VirtualSystemIdentifier>
                <vssd:VirtualSystemType>vmx-15</vssd:VirtualSystemType>
              </System>
              <Item>
                <rasd:Description>Number of Virtual CPUs</rasd:Description>
                <rasd:ElementName>2 virtual CPU(s)</rasd:ElementName>
                <rasd:InstanceID>1</rasd:InstanceID>
                <rasd:ResourceType>3</rasd:ResourceType>
                <rasd:VirtualQuantity>2</rasd:VirtualQuantity>
              </Item>
              <Item>
                <rasd:Description>Memory Size</rasd:Description>
                <rasd:ElementName>4096MB memory</rasd:ElementName>
                <rasd:InstanceID>2</rasd:InstanceID>
                <rasd:ResourceType>4</rasd:ResourceType>
                <rasd:VirtualQuantity>4096</rasd:VirtualQuantity>
              </Item>
            </VirtualHardwareSection>
          </VirtualSystem>
        </Envelope>
        """).strip() + "\n", encoding="utf-8")

        (output / "vm" / "README_VM.txt").write_text(textwrap.dedent("""
        AI Serviter VM Notes
        --------------------
        This OVF is a hardware profile scaffold. To create a real importable appliance:
        1. Install Ubuntu Server/Desktop in a VM.
        2. Copy this ISO/package into the VM.
        3. Install with scripts/install_unix.sh.
        4. Export the VM as OVF/OVA from your hypervisor.
        5. Attach the real disk reference to vm_config.ovf if packaging manually.
        """).strip() + "\n", encoding="utf-8")

    def write_readme(self, output: Path, app_name: str):
        (output / "README.txt").write_text(textwrap.dedent(f"""
        {app_name} ISO Package
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
        """).strip() + "\n", encoding="utf-8")
