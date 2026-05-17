@echo off
color 17
chcp 65001 > nul
setlocal enableextensions enabledelayedexpansion

cd /d "%~dp0..\..\.."

if not defined WMS_ORACLE_USER set "WMS_ORACLE_USER=RABAEV"
if not defined WMS_ORACLE_PASSWORD set "WMS_ORACLE_PASSWORD=RABAEVWMS"
if not defined WMS_ORACLE_DSN set "WMS_ORACLE_DSN=127.0.0.1:1521/orcl"

set "PYTHON_CMD=python.exe"
if exist "api\wms_api_server\.venv\Scripts\python.exe" set "PYTHON_CMD=api\wms_api_server\.venv\Scripts\python.exe"

echo Running BOM load test...
%PYTHON_CMD% tests\load\bom\bom_load_test.py --cleanup %*

if errorlevel 1 (
  color 4F
  echo BOM load test failed.
  pause
  exit /b 1
)

color 82
echo BOM load test finished.
pause
