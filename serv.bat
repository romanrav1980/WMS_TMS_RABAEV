@echo off
color 17
chcp 65001 > nul
setlocal enableextensions enabledelayedexpansion

set "API_PORT=8088"
set "API_HOST=0.0.0.0"
set "API_DIR=%~dp0api\wms_api_server"

if not defined WMS_ORACLE_USER set "WMS_ORACLE_USER=RABAEV"
if not defined WMS_ORACLE_PASSWORD set "WMS_ORACLE_PASSWORD=RABAEVWMS"
if not defined WMS_ORACLE_DSN set "WMS_ORACLE_DSN=127.0.0.1:1521/orcl"
if not defined WMS_CORS_ORIGINS set "WMS_CORS_ORIGINS=*"
if not defined WMS_API_AUDIT_ENABLED set "WMS_API_AUDIT_ENABLED=1"
if not defined WMS_API_AUDIT_LOCAL_DIR set "WMS_API_AUDIT_LOCAL_DIR=runtime\api_audit"
if not defined WMS_API_REPLAY_BASE_URL set "WMS_API_REPLAY_BASE_URL=http://127.0.0.1:%API_PORT%"
if not defined WMS_ADMIN_AUTH_ENABLED set "WMS_ADMIN_AUTH_ENABLED=1"

if not exist "%API_DIR%\app\main.py" (
  color 4F
  echo API server was not found: %API_DIR%
  pause
  exit /b 1
)

echo Checking port %API_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kill-port.ps1" -Port %API_PORT% -CommandLineLike "*uvicorn app.main:app*--port %API_PORT%*" -WaitSeconds 2 -FailIfBusy
if errorlevel 1 (
  color 4F
  echo API port cleanup failed.
  pause
  exit /b 1
)

cd /d "%API_DIR%"

set "PYTHON_CMD=python.exe"
if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=.venv\Scripts\python.exe"

echo Starting WMS API server...
echo   WMS_ORACLE_USER=%WMS_ORACLE_USER%
echo   WMS_ORACLE_DSN=%WMS_ORACLE_DSN%
echo   WMS_CORS_ORIGINS=%WMS_CORS_ORIGINS%
echo   WMS_API_AUDIT_ENABLED=%WMS_API_AUDIT_ENABLED%
echo   WMS_ADMIN_AUTH_ENABLED=%WMS_ADMIN_AUTH_ENABLED%
echo   Admin users are read from Oracle RUSERS/USER_GROUP/RIGHTS
echo   URL=http://127.0.0.1:%API_PORT%/docs
%PYTHON_CMD% -m uvicorn app.main:app --host %API_HOST% --port %API_PORT% --reload --no-use-colors

color 80
echo Server exited. You can close this window.
pause
exit /b
