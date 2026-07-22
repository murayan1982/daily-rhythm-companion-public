param(
    [switch]$ClearProviderKeys
)

$ErrorActionPreference = "Stop"

$names = @(
    "CONVERSATION_ENGINE",
    "SLEEP_PROVIDER",
    "FRAMEWORK_ROOT",
    "FRAMEWORK_PROJECT_ROOT",
    "FRAMEWORK_PRESET",
    "FRAMEWORK_CHARACTER",
    "FRAMEWORK_ADAPTER_MODE"
)

if ($ClearProviderKeys) {
    $names += @("GEMINI_API_KEY", "GOOGLE_API_KEY", "XAI_API_KEY")
}

foreach ($name in $names) {
    Remove-Item "Env:\$name" -ErrorAction SilentlyContinue
}

Write-Host "[framework-local-env] Cleared framework local environment variables."
if ($ClearProviderKeys) {
    Write-Host "[framework-local-env] Cleared provider API key environment variables from this PowerShell session."
} else {
    Write-Host "[framework-local-env] Provider API key environment variables were not changed. Pass -ClearProviderKeys to clear them too."
}
