@echo off
setlocal
set "TASK_ROOT=%~dp0"
set "TASK_PYTHON=%TASK_ROOT%api\wms_api_server\.venv\Scripts\python.exe"
if defined TMS_PYTHON_CMD set "TASK_PYTHON=%TMS_PYTHON_CMD%"
if not exist "%TASK_PYTHON%" (
  echo NICORA Python environment is missing.
  exit /b 1
)
cd /d "%TASK_ROOT%api\wms_api_server"
"%TASK_PYTHON%" -m app.workers.sap_artmas_worker --watch %*
