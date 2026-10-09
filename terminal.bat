@echo off
color 2F
chcp 65001 > nul
setlocal enableextensions enabledelayedexpansion

set "TERMINAL_PORT=3010"
set "TERMINAL_DIR=%~dp0terminal\wms_terminal_web"
set "VITE_WMS_API_BASE_URL=http://127.0.0.1:8088"
set "REACT_APP_API_BASE_URL=%VITE_WMS_API_BASE_URL%"
set "BROWSER=none"
if defined TMS_TERMINAL_PORT set "TERMINAL_PORT=%TMS_TERMINAL_PORT%"
if defined TMS_TERMINAL_FRONTEND_DIR set "TERMINAL_DIR=%TMS_TERMINAL_FRONTEND_DIR%"
if defined TMS_API_BASE_URL set "VITE_WMS_API_BASE_URL=%TMS_API_BASE_URL%"
set "REACT_APP_API_BASE_URL=%VITE_WMS_API_BASE_URL%"

if not exist "%TERMINAL_DIR%\package.json" (
  color 4F
  echo Terminal frontend was not found: %TERMINAL_DIR%
  pause
  exit /b 1
)

echo Checking port %TERMINAL_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kill-port.ps1" -Port %TERMINAL_PORT% -CommandLineLike "*--port %TERMINAL_PORT%*" -WaitSeconds 2 -FailIfBusy
if errorlevel 1 (
  color 4F
  echo Terminal port cleanup failed.
  pause
  exit /b 1
)

cd /d "%TERMINAL_DIR%"

echo Starting WMS terminal web app...
echo   VITE_WMS_API_BASE_URL=%VITE_WMS_API_BASE_URL%
echo   URL=http://127.0.0.1:%TERMINAL_PORT%/
npm.cmd run dev -- --port %TERMINAL_PORT% --strictPort

color 82
echo Terminal frontend exited. You can close this window.
pause
exit /b
