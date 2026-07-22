param(
    [string]$DayCheck = "",
    [switch]$SkipFlutter
)

$ErrorActionPreference = "Stop"

$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $Root

$VenvPython = Join-Path $Root "backend\.venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $Python = $VenvPython
} else {
    $Python = "python"
}

$LogDir = Join-Path $Root "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogPath = Join-Path $LogDir "agent_precommit_$Timestamp.log"

function Invoke-CheckStep {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host ""
    Write-Host "===== $Name ====="

    Add-Content -Path $LogPath -Value ""
    Add-Content -Path $LogPath -Value "===== $Name ====="

    $Global:LASTEXITCODE = 0
    & $Command 2>&1 | Tee-Object -FilePath $LogPath -Append

    if ($LASTEXITCODE -ne 0) {
        throw "FAILED: $Name (exit code: $LASTEXITCODE)"
    }
}

Invoke-CheckStep "compile backend" {
    & $Python -m compileall -q backend/app
}

Invoke-CheckStep "v0.34 baseline readiness" {
    & $Python scripts/check_v034_voice_input_release_readiness.py
}

if ($DayCheck -ne "") {
    if (-not (Test-Path $DayCheck)) {
        throw "DayCheck not found: $DayCheck"
    }

    Invoke-CheckStep "day check" {
        & $Python $DayCheck
    }
}

Invoke-CheckStep "backend api smoke" {
    & cmd.exe /c "backend\test_api.bat"
}

if (-not $SkipFlutter) {
    Invoke-CheckStep "flutter test" {
        Push-Location app
        try {
            & flutter test
        } finally {
            Pop-Location
        }
    }
}

Invoke-CheckStep "git diff summary" {
    & git status --short
    & git diff --stat
}

Write-Host ""
Write-Host "===== LOG SAVED ====="
Write-Host $LogPath
