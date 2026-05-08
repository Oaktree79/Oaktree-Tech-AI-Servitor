@echo off
echo AI Serviter Setup
echo ----------------------------------
echo.
echo 1. Install Python package locally
echo 2. Run API server
echo 3. View VM import instructions
echo 4. Exit
echo.
set /p choice="Enter your choice: "

if "%choice%"=="1" (
    cd app\python
    python -m pip install -e ".[dev]"
    pause
) else if "%choice%"=="2" (
    cd app\python
    serviter-service --root . --mode api --host 127.0.0.1 --port 8765
) else if "%choice%"=="3" (
    type vm\README_VM.txt
    pause
) else (
    exit
)
