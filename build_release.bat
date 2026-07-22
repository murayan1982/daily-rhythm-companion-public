@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Daily Rhythm Companion package builder.
REM DENYLIST_PACKAGE_BUILDER_VERSION=v7-release-surface-cleanup
REM DENYLIST_PACKAGE_BUILDER_HARDENING=v8-real-tts-secret-hygiene
REM DENYLIST_PACKAGE_BUILDER_HARDENING=v9-committed-head-worktree-git-file
REM
REM Policy:
REM   Package the project tree with a security denylist.
REM   Release mode no longer maintains a docs/scripts whitelist.
REM   Instead, copy everything except local secrets, tokens, private data,
REM   repository metadata, operator evidence, vendored dependencies, build/cache outputs, and generated release artifacts.
REM
REM Compatibility marker for older v1.0 checks:
REM   Exclude secrets, tokens, private local data, operator evidence, caches, build outputs, local handoff prompts, development-day docs/scripts, and release artifacts.
REM
REM Legacy compatibility markers kept for v1.0.x release checks:
REM   Copying root files
REM   Copying backend
REM   Copying Flutter app source
REM   Copying whitelisted docs
REM   Copying docs for handoff
REM   Copying root smoke/check scripts for handoff
REM
REM Usage:
REM   build_release.bat
REM   build_release.bat release
REM   build_release.bat handoff
REM   build_release.bat handoff v1.3.0_day1

set "MODE=%~1"
if "%MODE%"=="" set "MODE=release"
set "MODE=%MODE:"=%"

if /I not "%MODE%"=="release" if /I not "%MODE%"=="handoff" (
  echo [Error] Unknown mode: %MODE%
  echo Usage: %~nx0 [release^|handoff] [handoff_label]
  exit /b 1
)

set "HANDOFF_LABEL=%~2"
if "%HANDOFF_LABEL%"=="" set "HANDOFF_LABEL=v1.3.0_day1"
set "HANDOFF_LABEL=%HANDOFF_LABEL:"=%"

REM Run this script from anywhere; paths are resolved from this script location.
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TIMESTAMP=%%i"

set "RELEASE_DIR=%ROOT_DIR%release"
set "PACKAGE_ROOT_NAME=DailyRhythmCompanion"

REM Keep the temporary package directory outside the repository tree.
REM Robocopy fails with exit code 16 when copying a directory into its own child.
set "TEMP_BASE=%TEMP%"
if "%TEMP_BASE%"=="" set "TEMP_BASE=%SystemRoot%\Temp"
set "TEMP_ROOT=%TEMP_BASE%\DailyRhythmCompanion_release_temp_%TIMESTAMP%_%RANDOM%"
set "TEMP_DIR=%TEMP_ROOT%\%PACKAGE_ROOT_NAME%"
set "ROBOCOPY_LOG=%TEMP_ROOT%\robocopy_copy.log"

set "BUILD_STAGE=init"
set "ROBOCOPY_EXIT=0"

if /I "%MODE%"=="handoff" (
  set "ZIP_PATH=%RELEASE_DIR%\DailyRhythmCompanion_%HANDOFF_LABEL%_dev_handoff_%TIMESTAMP%.zip"
) else (
  set "ZIP_PATH=%RELEASE_DIR%\DailyRhythmCompanion_%TIMESTAMP%.zip"
)

echo ========================================
echo Daily Rhythm Companion - Package Builder
echo ========================================
echo Mode: %MODE%
echo Root: %ROOT_DIR%
echo Temp: %TEMP_ROOT%
echo Output: %ZIP_PATH%
echo.
echo Package policy:
echo   DENYLIST_PACKAGE_BUILDER_VERSION=v7-release-surface-cleanup
echo   DENYLIST_PACKAGE_BUILDER_HARDENING=v8-real-tts-secret-hygiene
echo   DENYLIST_PACKAGE_BUILDER_HARDENING=v9-committed-head-worktree-git-file
echo   Include project files by default.
echo   Exclude secrets, tokens, private local data, operator evidence, vendored dependencies, caches, build outputs, and release artifacts.
echo   Exclude secrets, tokens, private local data, operator evidence, caches, build outputs, local handoff prompts, development-day docs/scripts, and release artifacts. ^(legacy compatibility marker^)
echo.

set "BUILD_STAGE=setup_clean_temp"
echo [Setup] Cleaning temp directory...
call :cleanup_temp_silent

set "BUILD_STAGE=create_release_dir"
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"
if errorlevel 1 goto :fail

set "BUILD_STAGE=create_temp_dir"
mkdir "%TEMP_DIR%" >nul 2>nul
if errorlevel 1 (
  echo [Error] Failed to create temp directory: %TEMP_DIR%
  goto :fail
)

set "BUILD_STAGE=copy_project_tree"
echo [Copy] Copying project tree with security denylist...
echo [Copy] Copying root files... ^(legacy compatibility marker^)
echo [Copy] Copying backend... ^(legacy compatibility marker^)
echo [Copy] Copying Flutter app source... ^(legacy compatibility marker^)
echo [Copy] Copying whitelisted docs... ^(legacy compatibility marker; denylist policy is active^)
echo [Copy] Copying docs for handoff... ^(legacy compatibility marker^)
echo [Copy] Copying root smoke/check scripts for handoff... ^(legacy compatibility marker^)

robocopy "%ROOT_DIR%." "%TEMP_DIR%" /E ^
  /XD ^
    "%ROOT_DIR%.git" ^
    "%ROOT_DIR%release" ^
    "%ROOT_DIR%release_temp" ^
    "%ROOT_DIR%vendor" ^
    "%ROOT_DIR%docs\internal" ^
    "%ROOT_DIR%repo_files" ^
    "%ROOT_DIR%optional_replacements" ^
    "%ROOT_DIR%.venv" ^
    "%ROOT_DIR%venv" ^
    "%ROOT_DIR%app\build" ^
    "%ROOT_DIR%backend\local_data" ^
    "%ROOT_DIR%operator_evidence" ^
    "%ROOT_DIR%_local" ^
    "%ROOT_DIR%.release_build" ^
    ".git" ^
    "release" ^
    "release_temp" ^
    "vendor" ^
    "repo_files" ^
    "optional_replacements" ^
    ".venv" ^
    "venv" ^
    "env" ^
    "__pycache__" ^
    ".pytest_cache" ^
    ".mypy_cache" ^
    ".ruff_cache" ^
    ".dart_tool" ^
    ".pub-cache" ^
    ".gradle" ^
    ".idea" ^
    ".vscode" ^
    "build" ^
    "coverage" ^
    "ephemeral" ^
    ".plugin_symlinks" ^
    "local_data" ^
    "operator_evidence" ^
    "_local" ^
    ".release_build" ^
    "node_modules" ^
  /XF ^
    ".git" ^
    ".env" ^
    "*.local.env" ^
    "*.pem" ^
    "*.key" ^
    "*.p12" ^
    "*.pfx" ^
    "credentials.json" ^
    "client_secret*.json" ^
    "token.json" ^
    "*token*.json" ^
    "*tokens*.json" ^
    "*oauth_state*.json" ^
    "google_health_tokens.json" ^
    "google_health_oauth_state.json" ^
    "fitbit_tokens.json" ^
    "fitbit_oauth_state.json" ^
    "local.properties" ^
    "flutter_export_environment.sh" ^
    "Generated.xcconfig" ^
    ".flutter-plugins" ^
    ".flutter-plugins-dependencies" ^
    "*.pyc" ^
    "*.pyo" ^
    "*.log" ^
    "*.patch" ^
    "*.diff" ^
    "*.tmp" ^
    "*.bak" ^
    "*.swp" ^
    "*.swo" ^
    "*.sqlite" ^
    "*.sqlite3" ^
    "*.db" ^
    "*.db-journal" ^
    "*handoff*.md" ^
    "*next_thread_prompt*.md" ^
    "DRC_v190_Day22_handoff.md" ^
    "DRC_v190_next_thread_prompt.md" ^
    "DRC_v200_goal_checklist_small_commit_CommitC_ACCEPTED.md" ^
    "DAY*.md" ^
    "DOC_UPDATE_BUNDLE*.md" ^
    "README_B0_APPLY.md" ^
    "PATCH_SUMMARY.md" ^
    "VERIFICATION_SUMMARY.txt" ^
    "CHANGE_SUMMARY*" ^
    "IMPLEMENTATION_NOTES.txt" ^
    "LOCAL_VALIDATION_RESULT.txt" ^
    "README_LOCAL_ONLY.txt" ^
    "day*_validation.txt" ^
    "README_v*_day*.md" ^
    "check_v*_day*.py" ^
    "check_env_profile_v*_day*.py" ^
    "check_v190_smartphone_web_fw_demo_day*.py" ^
    "*.zip" ^
  /R:2 /W:1 /NFL /NDL /NP /NJH /NJS /LOG:"%ROBOCOPY_LOG%"
set "ROBOCOPY_EXIT=%ERRORLEVEL%"
if %ROBOCOPY_EXIT% GEQ 8 goto :robocopy_failed

REM Defense-in-depth: remove sensitive/local/generated files if they were copied by mistake.
set "BUILD_STAGE=sanitize"
echo [Sanitize] Removing local secrets, tokens, caches, generated artifacts, and release-only development artifacts...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop';" ^
  "$root = '%TEMP_DIR%';" ^
  "$dirNames = @('.git','release','release_temp','vendor','repo_files','optional_replacements','.venv','venv','env','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','.dart_tool','.pub-cache','.gradle','.idea','.vscode','build','coverage','ephemeral','.plugin_symlinks','local_data','operator_evidence','_local','.release_build','node_modules');" ^
  "$filePatterns = @('.git','*.pem','*.key','*.p12','*.pfx','credentials.json','client_secret*.json','token.json','*token*.json','*tokens*.json','*oauth_state*.json','google_health_tokens.json','google_health_oauth_state.json','fitbit_tokens.json','fitbit_oauth_state.json','local.properties','flutter_export_environment.sh','Generated.xcconfig','.flutter-plugins','.flutter-plugins-dependencies','*.pyc','*.pyo','*.log','*.patch','*.diff','*.tmp','*.bak','*.swp','*.swo','*.sqlite','*.sqlite3','*.db','*.db-journal','*handoff*.md','*next_thread_prompt*.md','DRC_v190_Day22_handoff.md','DRC_v190_next_thread_prompt.md','DRC_v200_goal_checklist_small_commit_CommitC_ACCEPTED.md','DAY*.md','DOC_UPDATE_BUNDLE*.md','README_B0_APPLY.md','PATCH_SUMMARY.md','VERIFICATION_SUMMARY.txt','CHANGE_SUMMARY*','IMPLEMENTATION_NOTES.txt','LOCAL_VALIDATION_RESULT.txt','README_LOCAL_ONLY.txt','day*_validation.txt','README_v*_day*.md','check_v*_day*.py','check_env_profile_v*_day*.py','check_v190_smartphone_web_fw_demo_day*.py','*.zip');" ^
  "if (Test-Path -LiteralPath $root) {" ^
  "  $docsInternal = Join-Path $root 'docs\internal';" ^
  "  if (Test-Path -LiteralPath $docsInternal) { Remove-Item -LiteralPath $docsInternal -Recurse -Force -ErrorAction SilentlyContinue };" ^
  "  foreach ($name in $dirNames) {" ^
  "    Get-ChildItem -LiteralPath $root -Recurse -Force -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -ieq $name } | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction SilentlyContinue };" ^
  "  }" ^
  "  Get-ChildItem -LiteralPath $root -Recurse -Force -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ieq '.env' -or $_.Name -like '*.local.env' -or ($_.Name -like '.env.*' -and $_.Name -notin @('.env.example','.env.sample','.env.template')) } | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue };" ^
  "  foreach ($pattern in $filePatterns) {" ^
  "    Get-ChildItem -LiteralPath $root -Recurse -Force -File -Filter $pattern -ErrorAction SilentlyContinue | ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force -ErrorAction SilentlyContinue };" ^
  "  }" ^
  "}"
if errorlevel 1 goto :fail

set "BUILD_STAGE=zip"
echo.
echo [Zip] Creating zip package...
if exist "%ZIP_PATH%" del /q "%ZIP_PATH%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; Compress-Archive -LiteralPath '%TEMP_DIR%' -DestinationPath '%ZIP_PATH%' -Force"
if errorlevel 1 goto :zip_failed
REM Give Compress-Archive / antivirus / indexers a moment to release file handles before cleanup.
timeout /t 1 /nobreak >nul

if not exist "%ZIP_PATH%" (
  echo [Error] Zip was not created: %ZIP_PATH%
  goto :fail
)
for %%z in ("%ZIP_PATH%") do if %%~zz LEQ 0 (
  echo [Error] Zip was created but is empty: %ZIP_PATH%
  goto :fail
)

set "BUILD_STAGE=cleanup_success"
echo.
echo [Cleanup] Removing temp directory...
call :cleanup_temp
if errorlevel 1 (
  echo [Warn] Package zip was created, but temp cleanup did not finish automatically.
  echo [Warn] You can remove it manually with:
  echo   powershell -NoProfile -Command "Remove-Item -LiteralPath '%TEMP_ROOT%' -Recurse -Force"
)

echo.
echo ========================================
echo Package created:
echo %ZIP_PATH%
echo ========================================
echo.
exit /b 0

:cleanup_temp_silent
if not exist "%TEMP_ROOT%" exit /b 0
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p = '%TEMP_ROOT%';" ^
  "if (-not (Test-Path -LiteralPath $p)) { exit 0 };" ^
  "try {" ^
  "  Get-ChildItem -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object { try { $_.Attributes = 'Normal' } catch {} };" ^
  "  Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction Stop;" ^
  "  exit 0;" ^
  "} catch { exit 0 }" >nul 2>nul
exit /b 0

:cleanup_temp
if not exist "%TEMP_ROOT%" exit /b 0
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$p = '%TEMP_ROOT%';" ^
  "for ($i = 1; $i -le 10; $i++) {" ^
  "  if (-not (Test-Path -LiteralPath $p)) { exit 0 }" ^
  "  try {" ^
  "    Get-ChildItem -LiteralPath $p -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object { try { $_.Attributes = 'Normal' } catch {} };" ^
  "    Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction Stop;" ^
  "    exit 0;" ^
  "  } catch {" ^
  "    Start-Sleep -Milliseconds 700;" ^
  "  }" ^
  "}" ^
  "if (Test-Path -LiteralPath $p) { exit 1 } else { exit 0 }"
if errorlevel 1 (
  echo [Warn] Failed to remove temp directory after retries: %TEMP_ROOT%
  exit /b 1
)
exit /b 0

:robocopy_failed
echo.
echo [Error] robocopy failed at stage: %BUILD_STAGE%
echo [Error] robocopy exit code: %ROBOCOPY_EXIT%
echo [Hint] This build file should print a Temp: line near the top. If it does not, the old file is still being run.
if exist "%ROBOCOPY_LOG%" (
  echo.
  echo [Robocopy log]
  type "%ROBOCOPY_LOG%"
)
echo.
goto :fail

:zip_failed
echo.
echo [Error] Failed to create package zip.
echo.
goto :fail

:fail
echo.
echo [Error] Package build failed at stage: %BUILD_STAGE%
echo [Cleanup] Attempting to remove temp directory after failure...
call :cleanup_temp
if errorlevel 1 exit /b 1
exit /b 1
