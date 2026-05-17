@echo off
color 17
chcp 65001 > nul
setlocal enableextensions enabledelayedexpansion

set "API_DIR=%~dp0api\wms_api_server"

if not defined WMS_ORACLE_USER set "WMS_ORACLE_USER=RABAEV"
if not defined WMS_ORACLE_PASSWORD set "WMS_ORACLE_PASSWORD=RABAEVWMS"
if not defined WMS_ORACLE_DSN set "WMS_ORACLE_DSN=127.0.0.1:1521/orcl"

if not exist "%API_DIR%\app\workers\outbox_worker.py" (
  color 4F
  echo Outbox worker was not found: %API_DIR%
  pause
  exit /b 1
)

echo Checking stale outbox worker processes...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kill-port.ps1" -CommandLineLike "*app.workers.outbox_worker*" -WaitSeconds 1
if errorlevel 1 (
  color 4F
  echo Worker cleanup failed.
  pause
  exit /b 1
)

cd /d "%API_DIR%"

set "PYTHON_CMD=python.exe"
if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=.venv\Scripts\python.exe"

echo Starting WMS external outbox worker...
echo   WMS_ORACLE_USER=%WMS_ORACLE_USER%
echo   WMS_ORACLE_DSN=%WMS_ORACLE_DSN%
%PYTHON_CMD% -m app.workers.outbox_worker --loop --sleep-seconds 5

color 80
echo Worker exited. You can close this window.
pause
