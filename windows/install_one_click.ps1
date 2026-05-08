$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root

Write-Host "AI Serviter One-Click Installer"
Write-Host "Root: $Root"

$Python = "python"
if (Test-Path "$Root\installer\runtime\python\python.exe") {
  $Python = "$Root\installer\runtime\python\python.exe"
}

& $Python -m venv .venv
& "$Root\.venv\Scripts\python.exe" -m pip install -U pip
& "$Root\.venv\Scripts\python.exe" -m pip install -e "$Root\python[dev]"
& "$Root\.venv\Scripts\python.exe" -m ai_serviter.one_click --root "$Root" setup
& "$Root\.venv\Scripts\python.exe" -m ai_serviter.one_click --root "$Root" launch

Write-Host "AI Serviter installed and launched."
