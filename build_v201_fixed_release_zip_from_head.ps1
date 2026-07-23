[CmdletBinding()]
param(
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
        throw "Working tree contains tracked or untracked changes. Commit or remove them before the fixed ZIP build."
    }

    $headCommit = (& git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or -not $headCommit) {
        throw "Unable to resolve committed HEAD."
    }

    $branchName = (& git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or $branchName -ne "main") {
        throw "The official v2.0.1 fixed ZIP must be built from Public main."
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
        throw "origin/main is unavailable. Run git fetch origin main --tags first."
    }
    if ($originMain -ne $headCommit) {
        throw "Public main HEAD does not match origin/main. Push or fetch before the fixed ZIP build."
    }

    $rootCommits = @(& git rev-list --max-parents=0 HEAD)
    if ($LASTEXITCODE -ne 0 -or $rootCommits.Count -ne 1) {
        throw "The official Public repository must have exactly one root commit."
    }

    $baselineTagOutput = @(& git tag --list "DRC_v2.0.0")
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect the immutable baseline tag."
    }
    $baselineTag = @($baselineTagOutput | Where-Object { $_ })
    if ($baselineTag.Count -ne 1) {
        throw "The immutable DRC_v2.0.0 baseline tag must remain present."
    }
    $baselineTagType = (& git cat-file -t "DRC_v2.0.0").Trim()
    if ($LASTEXITCODE -ne 0 -or $baselineTagType -ne "tag") {
        throw "DRC_v2.0.0 must remain an annotated tag."
    }

    $patchTagOutput = @(& git tag --list "DRC_v2.0.1")
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect existing patch tags."
    }
    $patchTag = @($patchTagOutput | Where-Object { $_ })
    if ($patchTag.Count -gt 0) {
        throw "DRC_v2.0.1 already exists. Refusing to build another fixed patch artifact."
    }

    $env:PYTHONDONTWRITEBYTECODE = "1"

    Write-Host "[Preflight] Running the strict final committed-source gate with Flutter..."
    Invoke-NativeChecked $PythonCommand `
        "scripts\check_v20x_patch_release.py" `
        "--source-tree" `
        "--with-flutter"

    $tempRoot = Join-Path (
        [IO.Path]::GetTempPath()
    ) ("DailyRhythmCompanion_v201_fixed_" + [Guid]::NewGuid().ToString("N"))
    $worktreeRoot = Join-Path $tempRoot "committed_head"
    New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

    Write-Host "[Source] Creating detached temporary worktree from Public committed HEAD..."
    & git worktree add --detach $worktreeRoot $headCommit
    if ($LASTEXITCODE -ne 0) {
        throw "git worktree add --detach failed."
    }
    $worktreeAdded = $true

    $worktreeHead = (& git -C $worktreeRoot rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0 -or $worktreeHead -ne $headCommit) {
        throw "Temporary worktree HEAD does not match the recorded Public source HEAD."
    }

    Write-Host "[Build] Invoking build_release.bat release exactly once from detached Public HEAD..."
    $buildInvocationCount++
    Push-Location $worktreeRoot
    try {
        & cmd.exe /d /c "build_release.bat release"
        if ($LASTEXITCODE -ne 0) {
            throw "build_release.bat release failed with exit code $LASTEXITCODE."
        }
    } finally {
        Pop-Location
    }

    if ($buildInvocationCount -ne 1) {
        throw "Fixed release builder invocation count was not exactly one."
    }

    $worktreeReleaseDirectory = Join-Path $worktreeRoot "release"
    $builtZips = @(
        Get-ChildItem -LiteralPath $worktreeReleaseDirectory `
            -File `
            -Filter "DailyRhythmCompanion_*.zip" `
            -ErrorAction Stop
    )
    if ($builtZips.Count -ne 1) {
        throw "Expected exactly one ZIP from the one build invocation, found $($builtZips.Count)."
    }

    $outputFullDirectory = if ([IO.Path]::IsPathRooted($OutputDirectory)) {
        [IO.Path]::GetFullPath($OutputDirectory)
    } else {
        [IO.Path]::GetFullPath((Join-Path $repoRoot $OutputDirectory))
    }
    $expectedOutputDirectory = [IO.Path]::GetFullPath((Join-Path $repoRoot "release"))
    if ($outputFullDirectory -ne $expectedOutputDirectory) {
        throw "The v2.0.1 fixed release ZIP must be written to the repository release directory."
    }
    New-Item -ItemType Directory -Path $outputFullDirectory -Force | Out-Null

    $destinationPath = Join-Path $outputFullDirectory $builtZips[0].Name
    if (Test-Path -LiteralPath $destinationPath) {
        throw "Destination ZIP already exists; refusing to overwrite a fixed artifact."
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
    Write-Host "v201_fixed_release_zip_build_status: built-once-from-clean-public-main"
    Write-Host "v201_fixed_release_zip_public_repository: murayan1982/daily-rhythm-companion-public"
    Write-Host "v201_fixed_release_zip_source_branch: $branchName"
    Write-Host "v201_fixed_release_zip_source_head: $headCommit"
    Write-Host "v201_fixed_release_zip_origin_main_head: $originMain"
    Write-Host "v201_fixed_release_zip_public_root_commit_count: $($rootCommits.Count)"
    Write-Host "v201_fixed_release_zip_build_invocation_count: $buildInvocationCount"
    Write-Host "v201_fixed_release_zip_path: $relativeZipPath"
    Write-Host "v201_fixed_release_zip_file_size_bytes: $($destinationFile.Length)"
    Write-Host "v201_fixed_release_zip_sha256: $sha256"
    Write-Host "v201_fixed_release_zip_verification_status: not-run"
    Write-Host "v201_fixed_release_zip_tag_created: False"
    Write-Host "v201_fixed_release_zip_github_release_created: False"
    Write-Host "v201_fixed_release_zip_next_action: verify-this-same-zip-without-rebuilding"
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
