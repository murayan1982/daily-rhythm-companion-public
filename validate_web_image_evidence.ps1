$ErrorActionPreference = "Stop"

$repoRoot = $PSScriptRoot
$day68 = Join-Path $repoRoot "operator_evidence\200_web_image_display_execution_day68.json"
$day79 = Join-Path $repoRoot "operator_evidence\200_web_image_display_screenshot_day79.json"

if (-not (Test-Path $day68)) {
    throw "Missing Day68 evidence file: $day68"
}
if (-not (Test-Path $day79)) {
    throw "Missing Day79 evidence file: $day79"
}

Push-Location $repoRoot
try {
    python scripts\smoke_framework_v200_web_image_display_execution_evidence.py `
      --operator-evidence-json $day68

    python scripts\smoke_framework_v200_web_image_display_screenshot_evidence.py `
      --evidence-json $day79
}
finally {
    Pop-Location
}
