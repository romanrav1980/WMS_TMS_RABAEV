@echo off
setlocal
cd /d "%~dp0"
echo RETAILCASE guide: http://127.0.0.1:4175/
echo Static documentation only. Press Ctrl+C to stop.
python -m http.server 4175 --bind 127.0.0.1
