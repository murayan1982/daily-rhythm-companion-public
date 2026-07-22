@echo off
setlocal

cd /d "%~dp0"

set INSTALL_OPTIONAL_FRAMEWORK_DEPS=0

if /i "%~1"=="--framework" (
    set INSTALL_OPTIONAL_FRAMEWORK_DEPS=1
)

if /i "%INSTALL_FRAMEWORK_DEPS%"=="1" (
    set INSTALL_OPTIONAL_FRAMEWORK_DEPS=1
)

echo ========================================
echo Daily Rhythm Companion API - Dev Server
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [Setup] Virtual environment not found.
    echo [Setup] Creating .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [Error] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [Setup] Activating virtual environment...
call ".venv\Scripts\activate.bat"

echo [Setup] Installing backend dependencies from requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [Error] Failed to install backend dependencies.
    pause
    exit /b 1
)

if "%INSTALL_OPTIONAL_FRAMEWORK_DEPS%"=="1" (
    echo [Setup] Installing optional framework dependencies...
    python -m pip install -r requirements-framework.txt
    if errorlevel 1 (
        echo [Error] Failed to install framework dependencies.
        pause
        exit /b 1
    )
) else (
    echo [Setup] Skipping optional framework dependencies.
    echo [Hint]  Run run_dev.bat --framework to install requirements-framework.txt.
)

echo.
echo [Start] Starting FastAPI dev server...
echo [URL]   http://127.0.0.1:8000
echo [Docs]  http://127.0.0.1:8000/docs
echo.
echo Press Ctrl+C to stop.
echo.

python -m uvicorn app.main:app --reload

echo.
echo [Stopped] FastAPI server stopped.
pause