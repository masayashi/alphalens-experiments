@echo off
setlocal

set UV_CACHE_DIR=.uv-cache
set PRE_COMMIT_HOME=.pre-commit-cache
set VIRTUALENV_OVERRIDE_APP_DATA=.virtualenv-cache

powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_quality_gate.ps1
if errorlevel 1 exit /b 1

exit /b 0
