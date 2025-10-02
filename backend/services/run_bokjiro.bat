@echo off
chcp 65001 >nul
echo ====================================
echo Bokjiro Scraper 실행
echo ====================================
echo.

cd /d "%~dp0"
python run_bokjiro_scraper.py %*

pause
