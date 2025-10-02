@echo off
chcp 65001 >nul
echo ====================================
echo Auto Scraper 실행
echo ====================================
echo.

cd /d "%~dp0"
python run_auto_scraper.py %*

pause
