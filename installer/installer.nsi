!include "MUI2.nsh"

Name "AI Serviter"
OutFile "AIServiter_Installer.exe"
InstallDir "$PROGRAMFILES\AIServiter"
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
    File /r "..\app\python\*"
    CreateShortCut "$DESKTOP\AI Serviter.lnk" "$INSTDIR\run_api.bat"
    FileOpen $0 "$INSTDIR\run_api.bat" w
    FileWrite $0 "@echo off$\r$\n"
    FileWrite $0 "python -m pip install -e .[dev]$\r$\n"
    FileWrite $0 "serviter-service --root . --mode api --host 127.0.0.1 --port 8765$\r$\n"
    FileClose $0
    WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\Uninstall.exe"
    Delete "$DESKTOP\AI Serviter.lnk"
    RMDir /r "$INSTDIR"
SectionEnd
