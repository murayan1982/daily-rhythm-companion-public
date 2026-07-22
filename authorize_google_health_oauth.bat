@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo Google Health OAuth Re-Authorization
echo ========================================
echo.

if not exist "backend\.venv\Scripts\python.exe" (
    echo [Error] backend\.venv was not found.
    echo [Hint]  Start backend\run_dev.bat once first, or create the backend virtual environment.
    pause
    exit /b 1
)

echo [Setup] Activating backend virtual environment...
call "backend\.venv\Scripts\activate.bat"

python scripts\authorize_google_health_oauth.py %*
set RESULT=%ERRORLEVEL%

echo.
if not "%RESULT%"=="0" (
    echo [Result] Google Health OAuth helper failed.
) else (
    echo [Result] Google Health OAuth helper completed.
)

pause
exit /b %RESULT%
