[CmdletBinding()]
param(
    [string]$OutputDirectory = "release",
    [string]$PythonCommand = "python",
    [Parameter(Mandatory = $true)]
    [string]$FlutterCommand,
    [switch]$PreflightOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$tempRoot = $null
$worktreeRoot = $null
$worktreeAdded = $false
$buildInvocationCount = 0
$previousDontWriteBytecode = $env:PYTHONDONTWRITEBYTECODE
$stage2AcceptedState = "Control D Stage 2:\s*`r?`nCLEAN_COMMITTED_SOURCE_PREFLIGHT / COMPLETED / PASS / ACCEPTED"
$stage3AuthorizationMarker = "Control D Stage 3:\s*`r?`nAUTHORIZED_FOR_ONE_TIME_BUILD"

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

function Get-RelativePathCompat {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BasePath,
        [Parameter(Mandatory = $true)]
        [string]$TargetPath
    )

    $baseFullPath = [IO.Path]::GetFullPath($BasePath)
    $targetFullPath = [IO.Path]::GetFullPath($TargetPath)
    $separator = [IO.Path]::DirectorySeparatorChar.ToString()
    if (-not $baseFullPath.EndsWith($separator)) {
        $baseFullPath += $separator
    }

    $baseUri = New-Object System.Uri($baseFullPath)
    $targetUri = New-Object System.Uri($targetFullPath)
    if ($baseUri.Scheme -ne $targetUri.Scheme) {
        return $targetFullPath
    }

    $relativeUri = $baseUri.MakeRelativeUri($targetUri)
    return [Uri]::UnescapeDataString($relativeUri.ToString()).Replace("/", $separator)
}

function Assert-AbsoluteFlutterCommand {
    param([Parameter(Mandatory = $true)][string]$Command)

    if (-not [IO.Path]::IsPathRooted($Command)) {
        throw "FlutterCommand must be an absolute command path; PATH lookup and bare flutter are forbidden."
    }
    $leaf = [IO.Path]::GetFileName($Command).ToLowerInvariant()
    if ($leaf -in @("flutter", "flutter.bat", "flutter.cmd") -and $Command -notmatch "[\\/]") {
        throw "Bare flutter is forbidden. Provide an absolute Flutter command path."
    }
    if (-not (Test-Path -LiteralPath $Command -PathType Leaf)) {
        throw "FlutterCommand does not exist: $Command"
    }
}

try {
    Push-Location $repoRoot
    Assert-AbsoluteFlutterCommand -Command $FlutterCommand

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
        throw "The official v4.0.0 fixed ZIP must be built from Public main."
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
        throw "origin/main is unavailable. Fetch is intentionally not performed by this builder."
    }
    if ($originMain -ne $headCommit) {
        throw "Public main HEAD does not match origin/main."
    }

    $rootCommits = @(& git rev-list --max-parents=0 HEAD)
    if ($LASTEXITCODE -ne 0 -or $rootCommits.Count -ne 1) {
        throw "The official Public repository must have exactly one root commit."
    }

    foreach ($tagName in @("DRC_v2.0.0", "DRC_v2.0.1", "DRC_v2.1.0", "DRC_v3.0.0")) {
        $tagOutput = @(& git tag --list $tagName)
        if ($LASTEXITCODE -ne 0) {
            throw "Unable to inspect immutable tag $tagName."
        }
        $tags = @($tagOutput | Where-Object { $_ })
        if ($tags.Count -ne 1) {
            throw "Immutable annotated tag $tagName must remain present."
        }
        $tagType = (& git cat-file -t $tagName).Trim()
        if ($LASTEXITCODE -ne 0 -or $tagType -ne "tag") {
            throw "$tagName must remain an annotated tag."
        }
    }

    if (@(& git tag --list "DRC_v4.0.0" | Where-Object { $_ }).Count -gt 0) {
        throw "DRC_v4.0.0 already exists. Refusing fixed ZIP tooling execution."
    }

    $outputFullDirectory = if ([IO.Path]::IsPathRooted($OutputDirectory)) {
        [IO.Path]::GetFullPath($OutputDirectory)
    } else {
        [IO.Path]::GetFullPath((Join-Path $repoRoot $OutputDirectory))
    }
    $expectedOutputDirectory = [IO.Path]::GetFullPath((Join-Path $repoRoot "release"))
    if ($outputFullDirectory -ne $expectedOutputDirectory) {
        throw "The v4.0.0 fixed release ZIP must be written to the repository release directory."
    }

    $existingV400Zips = @()
    if (Test-Path -LiteralPath $outputFullDirectory) {
        $existingV400Zips = @(
            Get-ChildItem -LiteralPath $outputFullDirectory `
                -File `
                -Filter "DailyRhythmCompanion_v4.0.0_*.zip" `
                -ErrorAction Stop
        )
    }
    if ($existingV400Zips.Count -gt 0) {
        throw "A v4.0.0 fixed ZIP already exists in release/. Refusing to build or overwrite another one."
    }

    $env:PYTHONDONTWRITEBYTECODE = "1"

    if ($PreflightOnly) {
        Write-Host "[Preflight] Running the strict Control D Stage 2 committed-source no-build gate..."
        Invoke-NativeChecked $PythonCommand `
            "scripts\check_v400_fixed_release_zip.py" `
            "--source-tree" `
            "--with-flutter" `
            "--with-builds" `
            "--flutter-command" `
            $FlutterCommand

        Write-Host ""
        Write-Host "========================================"
        Write-Host "v400_fixed_release_zip_preflight_status: passed-no-build"
        Write-Host "v400_fixed_release_zip_preflight_source_branch: $branchName"
        Write-Host "v400_fixed_release_zip_preflight_source_head: $headCommit"
        Write-Host "v400_fixed_release_zip_preflight_origin_main_head: $originMain"
        Write-Host "v400_fixed_release_zip_preflight_build_invocation_count: $buildInvocationCount"
        Write-Host "v400_fixed_release_zip_preflight_fixed_zip_built: False"
        Write-Host "v400_fixed_release_zip_preflight_tag_created: False"
        Write-Host "v400_fixed_release_zip_preflight_github_release_created: False"
        Write-Host "========================================"
        return
    }

    $protocolText = Get-Content -LiteralPath (Join-Path $repoRoot "docs\v400_release_preparation_protocol.md") -Raw
    $contractText = Get-Content -LiteralPath (Join-Path $repoRoot "docs\v400_fixed_release_zip.md") -Raw
    $authorizationText = $protocolText + "`n" + $contractText
    if ($authorizationText -notmatch $stage2AcceptedState) {
        throw "Actual fixed-ZIP build is blocked until Control D Stage 2 has been accepted."
    }
    if ($authorizationText -notmatch $stage3AuthorizationMarker) {
        throw "Actual fixed-ZIP build is blocked until Control D Stage 3 is explicitly authorized."
    }

    Write-Host "[Preflight] Running the strict Control D Stage 2 committed-source no-build gate..."
    Invoke-NativeChecked $PythonCommand `
        "scripts\check_v400_fixed_release_zip.py" `
        "--source-tree" `
        "--with-flutter" `
        "--with-builds" `
        "--flutter-command" `
        $FlutterCommand

    New-Item -ItemType Directory -Path $outputFullDirectory -Force | Out-Null
    $tempRoot = Join-Path (
        [IO.Path]::GetTempPath()
    ) ("DailyRhythmCompanion_v400_fixed_" + [Guid]::NewGuid().ToString("N"))
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

    $match = [regex]::Match($builtZips[0].Name, "^DailyRhythmCompanion_(\d{8}_\d{6})\.zip$")
    if (-not $match.Success) {
        throw "Unexpected generic builder ZIP name: $($builtZips[0].Name)"
    }

    $fixedBasename = "DailyRhythmCompanion_v4.0.0_$($match.Groups[1].Value).zip"
    $destinationPath = Join-Path $outputFullDirectory $fixedBasename
    if (Test-Path -LiteralPath $destinationPath) {
        throw "Destination ZIP already exists; refusing to overwrite the fixed artifact."
    }

    Move-Item -LiteralPath $builtZips[0].FullName -Destination $destinationPath

    $destinationFile = Get-Item -LiteralPath $destinationPath
    $sha256 = (Get-FileHash -LiteralPath $destinationPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $relativeZipPath = Get-RelativePathCompat -BasePath $repoRoot -TargetPath $destinationPath

    Write-Host ""
    Write-Host "========================================"
    Write-Host "v400_fixed_release_zip_build_status: built-once-from-clean-public-main"
    Write-Host "v400_fixed_release_zip_public_repository: murayan1982/daily-rhythm-companion-public"
    Write-Host "v400_fixed_release_zip_source_branch: $branchName"
    Write-Host "v400_fixed_release_zip_source_head: $headCommit"
    Write-Host "v400_fixed_release_zip_origin_main_head: $originMain"
    Write-Host "v400_fixed_release_zip_public_root_commit_count: $($rootCommits.Count)"
    Write-Host "v400_fixed_release_zip_build_invocation_count: $buildInvocationCount"
    Write-Host "v400_fixed_release_zip_path: $relativeZipPath"
    Write-Host "v400_fixed_release_zip_basename: $fixedBasename"
    Write-Host "v400_fixed_release_zip_file_size_bytes: $($destinationFile.Length)"
    Write-Host "v400_fixed_release_zip_sha256: $sha256"
    Write-Host "v400_fixed_release_zip_verification_status: not-run"
    Write-Host "v400_fixed_release_zip_tag_created: False"
    Write-Host "v400_fixed_release_zip_github_release_created: False"
    Write-Host "v400_fixed_release_zip_next_action: verify-this-same-zip-without-rebuilding"
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
