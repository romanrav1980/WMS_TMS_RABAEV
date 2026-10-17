@echo off
chcp 65001 > nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\start-retailcase-product.ps1" %*
if errorlevel 1 (
  echo Product launch failed. Check runtime\product-launch logs.
  pause
  exit /b 1
)
