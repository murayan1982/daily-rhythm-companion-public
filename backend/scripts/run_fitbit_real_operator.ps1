param(
    [string]$EnvFile = "",
    [string]$HostName = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$Reload,
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"

$BackendRoot = Split-Path -Parent $PSScriptRoot
$RepoRoot = Split-Path -Parent $BackendRoot

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
    $EnvFile = Join-Path $BackendRoot "env_profiles\fitbit_real_operator.local.env"
}

if (-not (Test-Path -LiteralPath $EnvFile -PathType Leaf)) {
    throw "Fitbit operator env file was not found."
}

$ResolvedEnvFile = (Resolve-Path -LiteralPath $EnvFile).Path

Push-Location $RepoRoot
try {
    Write-Host "[fitbit-operator-run] Validating public-safe operator env markers..."
    & python scripts\smoke_v210_fitbit_real_operator_preflight.py `
        --env-file $ResolvedEnvFile
    if ($LASTEXITCODE -ne 0) {
        throw "Fitbit operator env preflight failed."
    }
} finally {
    Pop-Location
}

$LoadedKeys = New-Object System.Collections.Generic.List[string]
foreach ($RawLine in [System.IO.File]::ReadAllLines($ResolvedEnvFile)) {
    $Line = $RawLine.Trim()
    if (-not $Line -or $Line.StartsWith("#")) {
        continue
    }

    $SeparatorIndex = $Line.IndexOf("=")
    if ($SeparatorIndex -lt 1) {
        throw "Operator env contains an invalid KEY=VALUE line."
    }

    $Key = $Line.Substring(0, $SeparatorIndex).Trim()
    $Value = $Line.Substring($SeparatorIndex + 1).Trim()

    if ($Key -notmatch '^[A-Z][A-Z0-9_]*$') {
        throw "Operator env contains an invalid key name."
    }

    [Environment]::SetEnvironmentVariable($Key, $Value, "Process")
    $LoadedKeys.Add($Key)
}

# Prevent backend/.env from overriding the validated dedicated profile.
[Environment]::SetEnvironmentVariable("DRC_SKIP_BACKEND_DOTENV", "1", "Process")

$RequiredExactValues = @{
    "CONVERSATION_ENGINE" = "mock"
    "SLEEP_PROVIDER" = "fitbit"
    "FITBIT_ENABLE_REAL_TOKEN_EXCHANGE" = "0"
    "FITBIT_DEV_SAVE_DUMMY_TOKEN" = "0"
}

foreach ($Entry in $RequiredExactValues.GetEnumerator()) {
    $Actual = [Environment]::GetEnvironmentVariable($Entry.Key, "Process")
    if ($Actual -ne $Entry.Value) {
        throw "Operator env runtime gate validation failed for key $($Entry.Key)."
    }
}

$TokenFile = Join-Path $BackendRoot "local_data\fitbit_tokens.json"
$TokenFileExists = Test-Path -LiteralPath $TokenFile -PathType Leaf
$SortedKeys = $LoadedKeys | Sort-Object -Unique

Write-Host "[fitbit-operator-run] operator_env_validation=accepted"
Write-Host "[fitbit-operator-run] backend_dotenv_override=disabled"
Write-Host "[fitbit-operator-run] token_file_exists=$TokenFileExists"
Write-Host "[fitbit-operator-run] loaded_key_names=$($SortedKeys -join ',')"

if ($ValidateOnly) {
    Write-Host "[fitbit-operator-run] validate_only=True"
    Write-Host "[fitbit-operator-run] backend_start=not-started"
    exit 0
}

$UvicornArgs = @(
    "-m",
    "uvicorn",
    "app.main:app",
    "--host",
    $HostName,
    "--port",
    $Port.ToString()
)
if ($Reload) {
    $UvicornArgs += "--reload"
}

throw "Legacy Fitbit Web API execution is retired. Use the Google Health API operator path."
