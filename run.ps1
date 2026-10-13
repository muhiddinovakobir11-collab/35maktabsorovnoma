# 35-Maktab So'rovnoma Portali - PowerShell Launcher
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $ScriptDir
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   35-Maktab So'rovnoma va Diagnostika Portali 2026" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Manzil: http://localhost:5000" -ForegroundColor Yellow
Write-Host "Admin parol: admin2026" -ForegroundColor Yellow
Write-Host ""
& "$ScriptDir\.venv\Scripts\python.exe" "$ScriptDir\app.py"
