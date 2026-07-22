param(
    [switch]$ClearProviderKeys,
    [switch]$CopyProfile
)

$ErrorActionPreference = "Stop"

$BackendRoot = Split-Path -Parent $PSScriptRoot
$MockSafeProfile = Join-Path $BackendRoot "env_profiles\mock_safe.env"
$EnvFile = Join-Path $BackendRoot ".env"

$env:CONVERSATION_ENGINE = "mock"
$env:SLEEP_PROVIDER = "mock"

$frameworkNames = @(
    "FRAMEWORK_ROOT",
    "FRAMEWORK_PROJECT_ROOT",
    "FRAMEWORK_PRESET",
    "FRAMEWORK_CHARACTER",
    "FRAMEWORK_ADAPTER_MODE"
)

foreach ($name in $frameworkNames) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
}

if ($ClearProviderKeys) {
    foreach ($name in @("GEMINI_API_KEY", "GOOGLE_API_KEY", "XAI_API_KEY")) {
        Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
    }
}

if ($CopyProfile) {
    if (-not (Test-Path $MockSafeProfile)) {
        throw "mock-safe profile not found: $MockSafeProfile"
    }
    Copy-Item $MockSafeProfile $EnvFile -Force
    Write-Host "[mock-safe-env] Copied backend\env_profiles\mock_safe.env to backend\.env."
}

Write-Host "[mock-safe-env] Set temporary mock-safe environment variables."
Write-Host "[mock-safe-env] CONVERSATION_ENGINE=$env:CONVERSATION_ENGINE"
Write-Host "[mock-safe-env] SLEEP_PROVIDER=$env:SLEEP_PROVIDER"

if ($ClearProviderKeys) {
    Write-Host "[mock-safe-env] Cleared provider API key environment variables from this PowerShell session."
} else {
    Write-Host "[mock-safe-env] Provider API key environment variables were not changed. Pass -ClearProviderKeys to clear them too."
}
