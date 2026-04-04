@echo off
title Swastik Pharmacy System
color 1F

echo.
echo  ============================================
echo   +  SWASTIK PHARMACY ^& SURGICAL CENTER
echo      Management System
echo  ============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Install from https://python.org
    pause
    exit /b
)

:: Install dependencies if needed
echo [1/4] Checking dependencies...
pip install -r requirements.txt -q

:: Run migrations
echo [2/4] Setting up database...
python manage.py migrate --run-syncdb -v 0

:: Check if medicines need importing
echo [3/4] Checking medicine data...
if exist "Swastik_Pharmacy.xlsx" (
    python manage.py import_medicines Swastik_Pharmacy.xlsx
) else (
    echo      [INFO] Place Swastik_Pharmacy.xlsx here to import medicines
)

:: Start server
echo [4/4] Starting server...
echo.
echo  ============================================
echo   Open in browser: http://127.0.0.1:8000
echo   For mobile: http://YOUR-IP:8000
echo   Press Ctrl+C to stop
echo  ============================================
echo.

python manage.py runserver 0.0.0.0:8000
pause
