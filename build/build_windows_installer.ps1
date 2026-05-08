$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root
if (!(Get-Command makensis -ErrorAction SilentlyContinue)) { throw "NSIS makensis not found." }
if (!(Test-Path "$Root\installer\runtime\python\python.exe")) {
  python "$Root\installer\runtime\fetch_python_runtime.py" --root "$Root"
}
makensis "$Root\installer\windows\AI-Serviter.nsi"
New-Item -ItemType Directory -Force -Path "$Root\release" | Out-Null
Copy-Item "$Root\installer\windows\AI-Serviter-Setup.exe" "$Root\release\AI-Serviter-Setup.exe" -ErrorAction SilentlyContinue
