@echo off
color 17
chcp 65001 > nul
setlocal enableextensions

echo Stopping WMS listeners...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop-listeners.ps1" %*
if errorlevel 1 (
  color 4F
  echo Listener cleanup failed.
  pause
  exit /b 1
)

color 80
echo Listener cleanup completed.
pause
exit /b 0
