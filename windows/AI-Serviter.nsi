!include "MUI2.nsh"

Name "AI Serviter"
OutFile "AI-Serviter-Setup.exe"
InstallDir "$LOCALAPPDATA\AI-Serviter"
RequestExecutionLevel user

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

Section "Install"
  SetOutPath "$INSTDIR"
  File /r "..\..\*"
  CreateShortCut "$DESKTOP\AI Serviter.lnk" "$INSTDIR\installer\windows\launch_ai_serviter.bat"
  ExecWait 'powershell -ExecutionPolicy Bypass -File "$INSTDIR\installer\windows\install_one_click.ps1"'
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\AI Serviter.lnk"
  RMDir /r "$INSTDIR"
SectionEnd
