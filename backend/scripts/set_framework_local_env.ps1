param(
    [string]$FrameworkRoot = "<path-to-ai-character-framework-development>",
    [string]$Preset = "text_chat",
    [string]$Character = "default",
    [string]$AdapterMode = "local_import"
)

$ErrorActionPreference = "Stop"

$env:CONVERSATION_ENGINE = "framework"
$env:SLEEP_PROVIDER = "mock"
$env:FRAMEWORK_ROOT = $FrameworkRoot
$env:FRAMEWORK_PRESET = $Preset
$env:FRAMEWORK_CHARACTER = $Character
$env:FRAMEWORK_ADAPTER_MODE = $AdapterMode

Write-Host "[framework-local-env] Set temporary framework local environment variables."
Write-Host "[framework-local-env] CONVERSATION_ENGINE=$env:CONVERSATION_ENGINE"
Write-Host "[framework-local-env] SLEEP_PROVIDER=$env:SLEEP_PROVIDER"
Write-Host "[framework-local-env] FRAMEWORK_ROOT=$env:FRAMEWORK_ROOT"
Write-Host "[framework-local-env] FRAMEWORK_PRESET=$env:FRAMEWORK_PRESET"
Write-Host "[framework-local-env] FRAMEWORK_CHARACTER=$env:FRAMEWORK_CHARACTER"
Write-Host "[framework-local-env] FRAMEWORK_ADAPTER_MODE=$env:FRAMEWORK_ADAPTER_MODE"

if (-not (Test-Path $FrameworkRoot)) {
    Write-Warning "[framework-local-env] FRAMEWORK_ROOT does not exist: $FrameworkRoot"
}

Write-Host "[framework-local-env] Provider API keys were not changed. Set them separately only when needed."
