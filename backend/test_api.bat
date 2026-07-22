@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

echo ========================================
echo Daily Rhythm Companion API - Test
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [Error] Virtual environment not found.
    echo Please run run_dev.bat first.
    pause
    exit /b 1
)

echo [Setup] Activating virtual environment...
call ".venv\Scripts\activate.bat"

echo [Preflight] Checking mock-safe environment profile...
python "..\scripts\check_env_profile.py" --profile mock-safe
if errorlevel 1 (
    echo.
    echo [Error] Environment profile check failed.
    echo [Hint]  For API smoke tests, copy:
    echo         backend\env_profiles\mock_safe.env
    echo         to backend\.env
    pause
    exit /b 1
)

echo.
echo [Test] Running API smoke test...
echo.

pwsh -NoProfile -ExecutionPolicy Bypass -File ".\scripts\test_api.ps1"

echo.
python "..\scripts\smoke_google_health_connection_ux_api.py"
if errorlevel 1 (
    echo.
    echo [Error] Google Health connection UX API smoke failed.
    pause
    exit /b 1
)

echo.
python "..\scripts\smoke_advice_recent_sleep_trend_api.py"
echo ========================================
echo Test finished.
echo ========================================
pause