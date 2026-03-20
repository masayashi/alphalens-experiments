$ErrorActionPreference = "Stop"

git config --local core.hooksPath .githooks

Write-Host "Configured local hooks path to .githooks"
Write-Host "Run this for full checks:"
Write-Host "  powershell -ExecutionPolicy Bypass -File scripts/run_quality_gate.ps1"
