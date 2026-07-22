[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$BaseUrl = "http://127.0.0.1:8000"

function Write-JsonResponse {
    param (
        [Parameter(Mandatory = $true)]
        [object] $Response
    )

    $Response | ConvertTo-Json -Depth 10
}

function New-CharacterPayload {
    param (
        [string] $CharacterId = "gentle_mina",
        [string] $DisplayName = "ミナ",
        [string] $PersonalityType = "gentle",
        [string] $SpeakingStyle = "casual",
        [string] $AdviceStyle = "rest_focused"
    )

    return @{
        character_id     = $CharacterId
        display_name     = $DisplayName
        personality_type = $PersonalityType
        speaking_style   = $SpeakingStyle
        advice_style     = $AdviceStyle
    }
}

function New-SleepPayload {
    param (
        [string] $QualityLabel,
        [bool] $Available = $true,
        [int] $TotalSleepMinutes = 372,
        [string] $Source = "mock",
        [bool] $IsRealData = $false,
        [string] $Confidence = "medium",
        [string] $Message = $null,
        [string] $UnavailableReason = $null
    )

    if (-not $Available) {
        return @{
            date                 = "2026-04-28"
            total_sleep_minutes  = 0
            efficiency           = $null
            deep_sleep_minutes   = $null
            rem_sleep_minutes    = $null
            awake_minutes        = $null
            source               = $Source
            available            = $false
            message              = if ($Message) { $Message } else { "Sleep data is unavailable for this smoke case." }
            sleep_start          = $null
            sleep_end            = $null
            quality_label        = $QualityLabel
            confidence           = "none"
            is_real_data         = $false
            unavailable_reason   = if ($UnavailableReason) { $UnavailableReason } else { "smoke_unavailable" }
        }
    }

    return @{
        date                 = "2026-04-28"
        total_sleep_minutes  = $TotalSleepMinutes
        efficiency           = 86
        deep_sleep_minutes   = 52
        rem_sleep_minutes    = 78
        awake_minutes        = 31
        source               = $Source
        available            = $true
        message              = "Mock sleep summary is available for this smoke case."
        sleep_start          = "2026-04-27T23:20:00"
        sleep_end            = "2026-04-28T05:32:00"
        quality_label        = $QualityLabel
        confidence           = $Confidence
        is_real_data         = $IsRealData
        unavailable_reason   = $null
    }
}

function Invoke-AdviceSmokeCase {
    param (
        [Parameter(Mandatory = $true)]
        [string] $CaseName,

        [Parameter(Mandatory = $true)]
        [hashtable] $Character,

        [Parameter(Mandatory = $true)]
        [hashtable] $Sleep,

        [Parameter(Mandatory = $true)]
        [string] $Mood
    )

    Write-Host ""
    Write-Host "=== POST /advice: $CaseName ==="

    $body = @{
        character = $Character
        sleep     = $Sleep
        mood      = $Mood
    } | ConvertTo-Json -Depth 10

    Invoke-RestMethod `
        -Uri "$BaseUrl/advice" `
        -Method Post `
        -ContentType "application/json; charset=utf-8" `
        -Body $body |
        ConvertTo-Json -Depth 10
}

Write-Host ""
Write-Host "=== GET /health ==="
Write-JsonResponse (Invoke-RestMethod "$BaseUrl/health")

Write-Host ""
Write-Host "=== GET /characters ==="
Write-JsonResponse (Invoke-RestMethod "$BaseUrl/characters")

Write-Host ""
Write-Host "=== GET /demo/status ==="
Write-JsonResponse (Invoke-RestMethod "$BaseUrl/demo/status")

Write-Host ""
Write-Host "=== GET /demo/voice-input/status ==="
Write-JsonResponse (Invoke-RestMethod "$BaseUrl/demo/voice-input/status")

Write-Host ""
Write-Host "=== POST /demo/voice-input: demo button metadata ==="
$voiceInputBody = @{
    client_event_id = "test-api-demo-button"
    input_mode      = "demo_button"
    text_hint       = "voice input demo smoke"
} | ConvertTo-Json -Depth 10
Write-JsonResponse (
    Invoke-RestMethod `
        -Uri "$BaseUrl/demo/voice-input" `
        -Method Post `
        -ContentType "application/json; charset=utf-8" `
        -Body $voiceInputBody
)

Write-Host ""
Write-Host "=== GET /sleep/summary ==="
Write-JsonResponse (Invoke-RestMethod "$BaseUrl/sleep/summary")

Write-Host ""
Write-Host "=== GET /fitbit/status ==="
Write-JsonResponse (Invoke-RestMethod "$BaseUrl/fitbit/status")

Write-Host ""
Write-Host "=== GET /fitbit/connect ==="
Write-JsonResponse (Invoke-RestMethod "$BaseUrl/fitbit/connect")

Write-Host ""
Write-Host "=== GET /fitbit/callback ==="
Write-JsonResponse (Invoke-RestMethod "$BaseUrl/fitbit/callback")

Write-Host ""
Write-Host "=== GET /fitbit/callback?code=dummy_code&state=invalid-state ==="
Write-JsonResponse (
    Invoke-RestMethod `
        -Uri "$BaseUrl/fitbit/callback?code=dummy_code&state=invalid-state"
)

Write-Host ""
Write-Host "=== GET /fitbit/callback?error=access_denied ==="
Write-JsonResponse (
    Invoke-RestMethod `
        -Uri "$BaseUrl/fitbit/callback?error=access_denied&error_description=User%20denied%20access"
)

$mina = New-CharacterPayload `
    -CharacterId "gentle_mina" `
    -DisplayName "ミナ" `
    -PersonalityType "gentle" `
    -SpeakingStyle "casual" `
    -AdviceStyle "rest_focused"

$sora = New-CharacterPayload `
    -CharacterId "cheerful_sora" `
    -DisplayName "ソラ" `
    -PersonalityType "cheerful" `
    -SpeakingStyle "casual" `
    -AdviceStyle "positive"

$rei = New-CharacterPayload `
    -CharacterId "cool_rei" `
    -DisplayName "レイ" `
    -PersonalityType "cool" `
    -SpeakingStyle "concise" `
    -AdviceStyle "practical"

Invoke-AdviceSmokeCase `
    -CaseName "short sleep + tired mood" `
    -Character $mina `
    -Sleep (New-SleepPayload -QualityLabel "short" -TotalSleepMinutes 320) `
    -Mood "tired"

Invoke-AdviceSmokeCase `
    -CaseName "short sleep + energetic mood" `
    -Character $sora `
    -Sleep (New-SleepPayload -QualityLabel "short" -TotalSleepMinutes 320) `
    -Mood "energetic"

Invoke-AdviceSmokeCase `
    -CaseName "good sleep + tired mood" `
    -Character $mina `
    -Sleep (New-SleepPayload -QualityLabel "good" -TotalSleepMinutes 490) `
    -Mood "tired"

Invoke-AdviceSmokeCase `
    -CaseName "good sleep + energetic mood" `
    -Character $sora `
    -Sleep (New-SleepPayload -QualityLabel "good" -TotalSleepMinutes 490) `
    -Mood "energetic"

Invoke-AdviceSmokeCase `
    -CaseName "fair sleep + tired mood" `
    -Character $rei `
    -Sleep (New-SleepPayload -QualityLabel "fair" -TotalSleepMinutes 410) `
    -Mood "tired"

Invoke-AdviceSmokeCase `
    -CaseName "unavailable sleep + tired mood" `
    -Character $mina `
    -Sleep (
        New-SleepPayload `
            -QualityLabel "unavailable" `
            -Available $false `
            -Message "Sleep data is unavailable for this smoke case." `
            -UnavailableReason "smoke_unavailable"
    ) `
    -Mood "tired"

Invoke-AdviceSmokeCase `
    -CaseName "unavailable sleep + energetic mood" `
    -Character $sora `
    -Sleep (
        New-SleepPayload `
            -QualityLabel "unavailable" `
            -Available $false `
            -Message "Sleep data is unavailable for this smoke case." `
            -UnavailableReason "smoke_unavailable"
    ) `
    -Mood "energetic"

Write-Host ""
Write-Host "=== GET /daily-records: after /advice auto-save ==="

(Invoke-WebRequest "$BaseUrl/daily-records").Content

Write-Host ""
Write-Host "=== POST /daily-records: manual save smoke ==="

$dailyRecordBody = @{
    date = "2026-05-08"
    character_id = "gentle_mina"
    character_name = "ミナ"
    mood = "tired"
    sleep_summary = @{
        date = "2026-05-08"
        total_sleep_minutes = 330
        efficiency = 82
        deep_sleep_minutes = $null
        rem_sleep_minutes = $null
        awake_minutes = $null
        source = "mock"
        available = $true
        message = "Mock sleep summary is available."
        sleep_start = $null
        sleep_end = $null
        quality_label = "short"
        confidence = "mock"
        is_real_data = $false
        unavailable_reason = $null
    }
    advice_message = "今日は回復優先でいきましょう。"
    advice_basis = "sleep+mood+character"
} | ConvertTo-Json -Depth 5

(Invoke-WebRequest `
    -Method Post `
    -Uri "$BaseUrl/daily-records" `
    -ContentType "application/json" `
    -Body $dailyRecordBody).Content

Write-Host ""
Write-Host "=== GET /daily-records/2026-05-08: manual save result ==="

(Invoke-WebRequest "$BaseUrl/daily-records/2026-05-08").Content

Write-Host ""
Write-Host "=== GET /daily-records: after manual save ==="

(Invoke-WebRequest "$BaseUrl/daily-records").Content