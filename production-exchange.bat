@echo off
color 17
chcp 65001 > nul
setlocal enableextensions enabledelayedexpansion

set "API_DIR=%~dp0api\wms_api_server"

if not defined WMS_ORACLE_USER set "WMS_ORACLE_USER=RABAEV"
if not defined WMS_ORACLE_PASSWORD set "WMS_ORACLE_PASSWORD=RABAEVWMS"
if not defined WMS_ORACLE_DSN set "WMS_ORACLE_DSN=127.0.0.1:1521/orcl"
if not defined WMS_PRODUCTION_EXCHANGE_ROOT_DIR set "WMS_PRODUCTION_EXCHANGE_ROOT_DIR=%~dp0exchange\production_release"

if not exist "%API_DIR%\app\workers\production_exchange_worker.py" (
  color 4F
  echo Production exchange worker was not found: %API_DIR%
  pause
  exit /b 1
)

echo Checking stale production exchange worker processes...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kill-port.ps1" -CommandLineLike "*app.workers.production_exchange_worker*" -WaitSeconds 1
if errorlevel 1 (
  color 4F
  echo Production exchange worker cleanup failed.
  pause
  exit /b 1
)

cd /d "%API_DIR%"

set "PYTHON_CMD=python.exe"
if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=.venv\Scripts\python.exe"

echo Starting WMS production release file exchange worker...
echo   WMS_ORACLE_USER=%WMS_ORACLE_USER%
echo   WMS_ORACLE_DSN=%WMS_ORACLE_DSN%
echo   WMS_PRODUCTION_EXCHANGE_ROOT_DIR=%WMS_PRODUCTION_EXCHANGE_ROOT_DIR%
%PYTHON_CMD% -m app.workers.production_exchange_worker --loop --sleep-seconds 5

color 80
echo Production exchange worker exited. You can close this window.
pause
