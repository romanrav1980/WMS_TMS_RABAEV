@echo off
cd /d "%~dp0api\wms_api_server"
.venv\Scripts\python.exe -m app.workers.sap_artmas_worker --kind supply --watch %*
