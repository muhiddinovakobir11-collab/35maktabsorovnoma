@echo off
title 35-Maktab So'rovnoma Portali
cd /d "%~dp0"
echo ========================================================
echo    35-Maktab So'rovnoma va Diagnostika Portali 2026
echo ========================================================
echo.
echo Server ishga tushirilmoqda...
echo Brauzerda ochish: http://localhost:5000
echo Admin parol: admin2026
echo.
call .venv\Scripts\activate.bat
python app.py
pause
