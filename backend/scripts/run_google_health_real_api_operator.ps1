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
    $EnvFile = Join-Path $BackendRoot "env_profiles\google_health_real_api_operator.local.env"
}

if (-not (Test-Path -LiteralPath $EnvFile -PathType Leaf)) {
    throw "Google Health operator env file was not found."
}

$ResolvedEnvFile = (Resolve-Path -LiteralPath $EnvFile).Path

Push-Location $RepoRoot
try {
    Write-Host "[google-health-operator-run] Validating public-safe operator env markers..."
    & python scripts\smoke_framework_v200_real_google_health_sleep_data_preflight.py `
        --env-file $ResolvedEnvFile
    if ($LASTEXITCODE -ne 0) {
        throw "Google Health operator env preflight failed."
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

# Prevent backend/.env from overriding the already validated operator profile.
[Environment]::SetEnvironmentVariable("DRC_SKIP_BACKEND_DOTENV", "1", "Process")

$RequiredExactValues = @{
    "CONVERSATION_ENGINE" = "mock"
    "SLEEP_PROVIDER" = "google_health"
    "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_EXCHANGE" = "0"
    "GOOGLE_HEALTH_ENABLE_REAL_TOKEN_REFRESH" = "1"
    "GOOGLE_HEALTH_ENABLE_REAL_API_REQUESTS" = "1"
    "GOOGLE_HEALTH_REAL_API_OPT_IN" = "1"
    "GOOGLE_HEALTH_REAL_ENDPOINT_VERIFIED" = "1"
}

foreach ($Entry in $RequiredExactValues.GetEnumerator()) {
    $Actual = [Environment]::GetEnvironmentVariable($Entry.Key, "Process")
    if ($Actual -ne $Entry.Value) {
        throw "Operator env runtime gate validation failed for key $($Entry.Key)."
    }
}

$CredentialsSetting = [Environment]::GetEnvironmentVariable(
    "GOOGLE_HEALTH_CREDENTIALS_FILE",
    "Process"
)
if ([string]::IsNullOrWhiteSpace($CredentialsSetting)) {
    throw "GOOGLE_HEALTH_CREDENTIALS_FILE is not configured."
}

$CredentialsPath = $CredentialsSetting
if (-not [System.IO.Path]::IsPathRooted($CredentialsPath)) {
    $CredentialsPath = Join-Path $BackendRoot $CredentialsPath
}
if (-not (Test-Path -LiteralPath $CredentialsPath -PathType Leaf)) {
    throw "Configured Google Health credentials file was not found."
}

$TokenFile = Join-Path $BackendRoot "local_data\google_health_tokens.json"
if (-not (Test-Path -LiteralPath $TokenFile -PathType Leaf)) {
    throw "Stored Google Health token file was not found."
}

$SortedKeys = $LoadedKeys | Sort-Object -Unique
Write-Host "[google-health-operator-run] operator_env_validation=accepted"
Write-Host "[google-health-operator-run] backend_dotenv_override=disabled"
Write-Host "[google-health-operator-run] credentials_file_exists=True"
Write-Host "[google-health-operator-run] token_file_exists=True"
Write-Host "[google-health-operator-run] loaded_key_names=$($SortedKeys -join ',')"

if ($ValidateOnly) {
    Write-Host "[google-health-operator-run] validate_only=True"
    Write-Host "[google-health-operator-run] backend_start=not-started"
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

Write-Host "[google-health-operator-run] Starting actual DRC backend API."
Write-Host "[google-health-operator-run] Host and private network details must remain local-only."

Push-Location $BackendRoot
try {
    & python @UvicornArgs
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
