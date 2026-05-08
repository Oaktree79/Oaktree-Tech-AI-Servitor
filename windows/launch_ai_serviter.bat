@echo off
cd /d "%~dp0\..\.."
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m ai_serviter.one_click --root "%CD%" launch
) else (
  powershell -ExecutionPolicy Bypass -File installer\windows\install_one_click.ps1
)
