[CmdletBinding()]
param(
    [string]$ManifestPath = "operator_evidence\v200_accepted_web_evidence_manifest_day80.json",
    [string]$OutputDirectory = "release",
    [string]$PythonCommand = "python"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$tempRoot = $null
$worktreeRoot = $null
$worktreeAdded = $false
$buildInvocationCount = 0

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$ArgumentList
    )

    & $FilePath @ArgumentList
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($ArgumentList -join ' ')"
    }
}

try {
    Push-Location $repoRoot

    $gitRoot = (& git rev-parse --show-toplevel).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $gitRoot) {
        throw "This script must run from a Git working tree."
    }
    if ([IO.Path]::GetFullPath($gitRoot) -ne [IO.Path]::GetFullPath($repoRoot)) {
        throw "Repository root mismatch. Script root: $repoRoot ; Git root: $gitRoot"
    }

    $dirtyState = @(& git status --porcelain --untracked-files=all)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect Git working tree state."
    }
    if ($dirtyState.Count -gt 0) {
        throw "Working tree contains tracked or non-ignored uncommitted files. Commit or remove them before the final fixed zip build."
    }

    $headCommit = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $headCommit) {
        throw "Unable to resolve committed HEAD."
    }
    $branchName = (& git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to resolve the current branch."
    }
    if (-not $branchName) {
        $branchName = "detached"
    }

    $manifestFullPath = if ([IO.Path]::IsPathRooted($ManifestPath)) {
        [IO.Path]::GetFullPath($ManifestPath)
    } else {
        [IO.Path]::GetFullPath((Join-Path $repoRoot $ManifestPath))
    }
    if (-not (Test-Path -LiteralPath $manifestFullPath -PathType Leaf)) {
        throw "Accepted Day80 private manifest was not found at the configured ignored operator path."
    }

    Write-Host "[Preflight] Verifying Public distribution source surface..."
    Invoke-NativeChecked $PythonCommand "scripts\smoke_framework_v200_public_distribution_readiness.py"

    Write-Host "[Preflight] Verifying committed G-5 public-safe acceptance state..."
    Invoke-NativeChecked $PythonCommand "scripts\smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py"

    Write-Host "[Preflight] Validating the ignored Day80 private manifest..."
    Invoke-NativeChecked $PythonCommand "scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py" "--manifest-json" $manifestFullPath

    $tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("DailyRhythmCompanion_v200_fixed_" + [Guid]::NewGuid().ToString("N"))
    $worktreeRoot = Join-Path $tempRoot "committed_head"
    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

    Write-Host "[Source] Creating detached temporary worktree from committed HEAD..."
    Invoke-NativeChecked "git" "worktree" "add" "--detach" $worktreeRoot $headCommit
    $worktreeAdded = $true

    $worktreeHead = (& git -C $worktreeRoot rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $worktreeHead -ne $headCommit) {
        throw "Temporary worktree HEAD does not match the recorded source HEAD."
    }

    Write-Host "[Build] Invoking build_release.bat exactly once from detached committed HEAD..."
    $buildInvocationCount++
    Push-Location $worktreeRoot
    try {
        & cmd.exe /d /c "build_release.bat release"
        if ($LASTEXITCODE -ne 0) {
            throw "build_release.bat failed with exit code $LASTEXITCODE."
        }
    } finally {
        Pop-Location
    }

    if ($buildInvocationCount -ne 1) {
        throw "Final fixed release builder invocation count was not exactly one."
    }

    $worktreeReleaseDirectory = Join-Path $worktreeRoot "release"
    $builtZips = @(
        Get-ChildItem -LiteralPath $worktreeReleaseDirectory -File -Filter "DailyRhythmCompanion_*.zip" -ErrorAction Stop
    )
    if ($builtZips.Count -ne 1) {
        throw "Expected exactly one release zip from the one build invocation, found $($builtZips.Count)."
    }

    $outputFullDirectory = if ([IO.Path]::IsPathRooted($OutputDirectory)) {
        [IO.Path]::GetFullPath($OutputDirectory)
    } else {
        [IO.Path]::GetFullPath((Join-Path $repoRoot $OutputDirectory))
    }
    $expectedOutputDirectory = [IO.Path]::GetFullPath((Join-Path $repoRoot "release"))
    if ($outputFullDirectory -ne $expectedOutputDirectory) {
        throw "The final fixed release zip must be written to the repository release directory."
    }
    New-Item -ItemType Directory -Path $outputFullDirectory -Force | Out-Null

    $destinationPath = Join-Path $outputFullDirectory $builtZips[0].Name
    if (Test-Path -LiteralPath $destinationPath) {
        throw "Destination release zip already exists; refusing to overwrite a fixed artifact."
    }
    Move-Item -LiteralPath $builtZips[0].FullName -Destination $destinationPath

    $destinationFile = Get-Item -LiteralPath $destinationPath
    $sha256 = (Get-FileHash -LiteralPath $destinationPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $relativeZipPath = [IO.Path]::GetRelativePath($repoRoot, $destinationPath).Replace([IO.Path]::AltDirectorySeparatorChar, [IO.Path]::DirectorySeparatorChar)

    Write-Host ""
    Write-Host "========================================"
    Write-Host "v200_final_fixed_release_zip_build_status: built-once-from-committed-head"
    Write-Host "v200_final_fixed_release_zip_source_branch: $branchName"
    Write-Host "v200_final_fixed_release_zip_source_head: $headCommit"
    Write-Host "v200_final_fixed_release_zip_build_invocation_count: $buildInvocationCount"
    Write-Host "v200_final_fixed_release_zip_path: $relativeZipPath"
    Write-Host "v200_final_fixed_release_zip_file_size_bytes: $($destinationFile.Length)"
    Write-Host "v200_final_fixed_release_zip_sha256: $sha256"
    Write-Host "v200_final_fixed_release_zip_verification_status: not-run"
    Write-Host "v200_final_fixed_release_zip_next_action: verify-this-same-zip-without-rebuilding"
    Write-Host "========================================"
} finally {
    if ($worktreeAdded -and $worktreeRoot) {
        & git -C $repoRoot worktree remove --force $worktreeRoot 2>$null | Out-Null
        & git -C $repoRoot worktree prune 2>$null | Out-Null
    }
    if ($tempRoot -and (Test-Path -LiteralPath $tempRoot)) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    Pop-Location
}
