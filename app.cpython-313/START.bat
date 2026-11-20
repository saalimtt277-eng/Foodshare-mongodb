@echo off
cd /d "%~dp0"
echo FOODSHARE - Installing Python requirements...
py -m pip install -r requirements.txt
if errorlevel 1 (
    echo Installation failed. Ensure Python is installed and select Add Python to PATH.
    pause
    exit /b 1
)
echo.
echo Starting FoodShare. Keep this window OPEN.
echo Open http://127.0.0.1:5000 in Chrome.
py app.py
pause
