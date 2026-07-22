$ErrorActionPreference = "Stop"

python scripts\smoke_framework_v200_real_tts_web_audio_output_evidence.py `
  --operator-evidence-json `
  operator_evidence\200_real_tts_web_audio_day54.json

python scripts\smoke_framework_v200_real_tts_web_audio_execution_evidence.py `
  --operator-evidence-json `
  operator_evidence\200_real_tts_web_audio_day65.json

python scripts\smoke_framework_v200_real_tts_web_audio_screenshot_evidence.py `
  --evidence-json `
  operator_evidence\200_real_tts_web_audio_day77.json

python scripts\smoke_framework_v200_real_tts_web_audio_acceptance.py `
  --day54-json operator_evidence\200_real_tts_web_audio_day54.json `
  --day65-json operator_evidence\200_real_tts_web_audio_day65.json `
  --day77-json operator_evidence\200_real_tts_web_audio_day77.json
