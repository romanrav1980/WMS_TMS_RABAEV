@echo off
color 27
chcp 65001 > nul
setlocal enableextensions enabledelayedexpansion

set "FRONT_PORT=3000"
set "REACT_APP_API_BASE_URL=http://127.0.0.1:8088"
set "BROWSER=none"
set "PORT=%FRONT_PORT%"

set "REACT_FRONT_DIR=%~dp0admin\wms_admin_frontend"
set "RAW_FRONT_DIR=%~dp0wiki-raw\wms_admin_ui_reference"

echo Checking port %FRONT_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kill-port.ps1" -Port %FRONT_PORT% -CommandLineLike "*http.server %FRONT_PORT%*" -CommandLineLike "*--port %FRONT_PORT%*" -WaitSeconds 2 -FailIfBusy
if errorlevel 1 (
  color 4F
  echo Frontend port cleanup failed.
  pause
  exit /b 1
)

if exist "%REACT_FRONT_DIR%\package.json" (
  cd /d "%REACT_FRONT_DIR%"
  echo Starting WMS admin frontend...
  echo   REACT_APP_API_BASE_URL=%REACT_APP_API_BASE_URL%
  echo   PORT=%PORT%
  npm start
) else (
  cd /d "%RAW_FRONT_DIR%"
  echo React admin frontend is not created yet.
  echo Starting raw WMS admin UI reference...
  echo   URL=http://127.0.0.1:%FRONT_PORT%/
  python -m http.server %FRONT_PORT% --bind 127.0.0.1
)

color 82
echo Front exited. You can close this window.
pause
exit /b
