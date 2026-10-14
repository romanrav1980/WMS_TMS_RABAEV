@echo off
chcp 65001 > nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\install-retail-case.ps1" %*
if errorlevel 1 (
  echo Installation failed. Read the error above and docs\install-retail-case.md.
  pause
  exit /b 1
)
pause
