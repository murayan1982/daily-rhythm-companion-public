[CmdletBinding()]
param(
    [string]$ManifestPath = "",
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
$previousDontWriteBytecode = $env:PYTHONDONTWRITEBYTECODE

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

function Test-PathOutsideRepository {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepositoryRoot,
        [Parameter(Mandatory = $true)]
        [string]$CandidatePath
    )

    $relative = [IO.Path]::GetRelativePath(
        [IO.Path]::GetFullPath($RepositoryRoot),
        [IO.Path]::GetFullPath($CandidatePath)
    )
    if ([IO.Path]::IsPathRooted($relative)) {
        return $true
    }

    $parentPrefix = ".." + [IO.Path]::DirectorySeparatorChar
    $altParentPrefix = ".." + [IO.Path]::AltDirectorySeparatorChar
    return (
        $relative -eq ".." -or
        $relative.StartsWith($parentPrefix, [StringComparison]::Ordinal) -or
        $relative.StartsWith($altParentPrefix, [StringComparison]::Ordinal)
    )
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
    if ($LASTEXITCODE -ne 0 -or $branchName -ne "main") {
        throw "The official Public fixed zip must be built from the Public main branch."
    }

    $originUrl = (& git remote get-url origin).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $originUrl) {
        throw "The official Public repository must have an origin remote."
    }
    $officialOriginPattern = "^(?:https://github\.com/|git@github\.com:)murayan1982/daily-rhythm-companion-public(?:\.git)?$"
    if ($originUrl -notmatch $officialOriginPattern) {
        throw "Origin is not the official Public repository."
    }

    $originMain = (& git rev-parse refs/remotes/origin/main).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $originMain) {
        throw "origin/main is unavailable. Fetch origin/main before the final build."
    }
    if ($originMain -ne $headCommit) {
        throw "Public main HEAD does not match origin/main. Push or fetch before the final build."
    }

    $rootCommits = @(& git rev-list --max-parents=0 HEAD)
    if ($LASTEXITCODE -ne 0 -or $rootCommits.Count -ne 1) {
        throw "The official Public repository must have exactly one root commit."
    }

    $existingTag = (& git tag --list "DRC_v2.0.0").Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect existing tags."
    }
    if ($existingTag) {
        throw "DRC_v2.0.0 already exists locally. Refusing to build another final artifact."
    }

    if ([string]::IsNullOrWhiteSpace($ManifestPath)) {
        throw "ManifestPath is required and must point to the accepted Day80 manifest outside the Public repository."
    }
    $manifestFullPath = if ([IO.Path]::IsPathRooted($ManifestPath)) {
        [IO.Path]::GetFullPath($ManifestPath)
    } else {
        [IO.Path]::GetFullPath((Join-Path $repoRoot $ManifestPath))
    }
    if (-not (Test-Path -LiteralPath $manifestFullPath -PathType Leaf)) {
        throw "Accepted Day80 private manifest was not found."
    }
    if (-not (Test-PathOutsideRepository -RepositoryRoot $repoRoot -CandidatePath $manifestFullPath)) {
        throw "The accepted Day80 manifest must remain outside the Public repository."
    }

    $env:PYTHONDONTWRITEBYTECODE = "1"

    Write-Host "[Preflight] Verifying the complete Public source directory strictly..."
    Invoke-NativeChecked $PythonCommand `
        "scripts\smoke_framework_v200_public_distribution_readiness.py" `
        "--source-directory" `
        $repoRoot

    Write-Host "[Preflight] Verifying committed public-safe acceptance state..."
    Invoke-NativeChecked $PythonCommand `
        "scripts\smoke_framework_v200_accepted_web_evidence_manifest_acceptance_sync.py"

    Write-Host "[Preflight] Validating the external Day80 private manifest..."
    Invoke-NativeChecked $PythonCommand `
        "scripts\smoke_framework_v200_accepted_web_evidence_manifest_aggregate.py" `
        "--manifest-json" `
        $manifestFullPath

    $tempRoot = Join-Path (
        [IO.Path]::GetTempPath()
    ) ("DailyRhythmCompanion_v200_fixed_" + [Guid]::NewGuid().ToString("N"))
    $worktreeRoot = Join-Path $tempRoot "committed_head"
    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

    Write-Host "[Source] Creating detached temporary worktree from Public committed HEAD..."
    Invoke-NativeChecked "git" "worktree" "add" "--detach" $worktreeRoot $headCommit
    $worktreeAdded = $true

    $worktreeHead = (& git -C $worktreeRoot rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $worktreeHead -ne $headCommit) {
        throw "Temporary worktree HEAD does not match the recorded Public source HEAD."
    }

    Write-Host "[Build] Invoking build_release.bat exactly once from detached Public HEAD..."
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
        Get-ChildItem -LiteralPath $worktreeReleaseDirectory `
            -File `
            -Filter "DailyRhythmCompanion_*.zip" `
            -ErrorAction Stop
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
    $sha256 = (
        Get-FileHash -LiteralPath $destinationPath -Algorithm SHA256
    ).Hash.ToLowerInvariant()
    $relativeZipPath = [IO.Path]::GetRelativePath(
        $repoRoot,
        $destinationPath
    ).Replace(
        [IO.Path]::AltDirectorySeparatorChar,
        [IO.Path]::DirectorySeparatorChar
    )

    Write-Host ""
    Write-Host "========================================"
    Write-Host "v200_final_fixed_release_zip_build_status: built-once-from-clean-public-main"
    Write-Host "v200_final_fixed_release_zip_repository_topology: clean-history-public-snapshot"
    Write-Host "v200_final_fixed_release_zip_public_repository: murayan1982/daily-rhythm-companion-public"
    Write-Host "v200_final_fixed_release_zip_source_branch: $branchName"
    Write-Host "v200_final_fixed_release_zip_source_head: $headCommit"
    Write-Host "v200_final_fixed_release_zip_origin_main_head: $originMain"
    Write-Host "v200_final_fixed_release_zip_public_root_commit_count: $($rootCommits.Count)"
    Write-Host "v200_final_fixed_release_zip_external_day80_manifest: True"
    Write-Host "v200_final_fixed_release_zip_build_invocation_count: $buildInvocationCount"
    Write-Host "v200_final_fixed_release_zip_path: $relativeZipPath"
    Write-Host "v200_final_fixed_release_zip_file_size_bytes: $($destinationFile.Length)"
    Write-Host "v200_final_fixed_release_zip_sha256: $sha256"
    Write-Host "v200_final_fixed_release_zip_verification_status: not-run"
    Write-Host "v200_final_fixed_release_zip_next_action: verify-this-same-zip-without-rebuilding"
    Write-Host "========================================"
} finally {
    if ([string]::IsNullOrEmpty($previousDontWriteBytecode)) {
        Remove-Item Env:PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue
    } else {
        $env:PYTHONDONTWRITEBYTECODE = $previousDontWriteBytecode
    }

    if ($worktreeAdded -and $worktreeRoot) {
        & git -C $repoRoot worktree remove --force $worktreeRoot 2>$null | Out-Null
        & git -C $repoRoot worktree prune 2>$null | Out-Null
    }
    if ($tempRoot -and (Test-Path -LiteralPath $tempRoot)) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    Pop-Location
}
