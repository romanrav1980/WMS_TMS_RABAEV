@echo off
color 27
chcp 65001 > nul
setlocal enableextensions enabledelayedexpansion

set "PROJECT_CONFIG=%~dp0config\project.defaults.json"
for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "(Get-Content -Raw '%PROJECT_CONFIG%' | ConvertFrom-Json).local.loopbackHost"`) do set "LOCAL_HOST=%%A"
for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "(Get-Content -Raw '%PROJECT_CONFIG%' | ConvertFrom-Json).local.frontendPort"`) do set "FRONT_PORT=%%A"
for /f "usebackq delims=" %%A in (`powershell -NoProfile -Command "(Get-Content -Raw '%PROJECT_CONFIG%' | ConvertFrom-Json).local.apiPort"`) do set "API_PORT=%%A"

if defined TMS_LOCAL_HOST set "LOCAL_HOST=%TMS_LOCAL_HOST%"
if defined TMS_FRONTEND_PORT set "FRONT_PORT=%TMS_FRONTEND_PORT%"
if defined TMS_API_PORT set "API_PORT=%TMS_API_PORT%"

set "TMS_LOCAL_HOST=%LOCAL_HOST%"
set "TMS_FRONTEND_PORT=%FRONT_PORT%"
set "TMS_API_PORT=%API_PORT%"
set "VITE_API_BASE=http://%LOCAL_HOST%:%API_PORT%"
set "VITE_ADMIN_BASIC_AUTH=admin:admin123"
set "BROWSER=none"
set "PORT=%FRONT_PORT%"

set "REACT_FRONT_DIR=%~dp0admin\wms_admin_frontend"
set "RAW_FRONT_DIR=%~dp0wiki-raw\wms_admin_ui_reference"

echo Checking port %FRONT_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kill-port.ps1" -Port %FRONT_PORT% -CommandLineLike "*http.server %FRONT_PORT%*","*--port %FRONT_PORT%*" -WaitSeconds 2 -FailIfBusy
if errorlevel 1 (
  color 4F
  echo Frontend port cleanup failed.
  pause
  exit /b 1
)

if exist "%REACT_FRONT_DIR%\package.json" (
  cd /d "%REACT_FRONT_DIR%"
  echo Starting WMS admin frontend...
  echo   VITE_API_BASE=%VITE_API_BASE%
  echo   PORT=%PORT%
  npm.cmd run start
) else (
  cd /d "%RAW_FRONT_DIR%"
  echo React admin frontend is not created yet.
  echo Starting raw WMS admin UI reference...
  echo   URL=http://%LOCAL_HOST%:%FRONT_PORT%/
  python -m http.server %FRONT_PORT% --bind %LOCAL_HOST%
)

color 82
echo Front exited. You can close this window.
pause
exit /b
