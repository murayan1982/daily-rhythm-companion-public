#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
revision=4ecc2ba63bcac23ba4a767fc87025b1450f84c9c
source_url="https://huggingface.co/google/gemma-4-E4B-it/resolve/$revision"
staging=$(mktemp -d)
trap 'rm -rf "$staging"' EXIT

for artifact in tokenizer.json chat_template.jinja; do
    curl --fail --silent --show-error --location --max-time 120 \
        "$source_url/$artifact" --output "$staging/$artifact"
done

python - "$staging" <<'PY'
from pathlib import Path
import sys

from app.services.public_advice_startup import load_gemini_input_counter

load_gemini_input_counter(Path(sys.argv[1]))
print("Gemini tokenizer files verified.")
PY

mkdir -p .gemini-tokenizer
mv "$staging/tokenizer.json" "$staging/chat_template.jinja" .gemini-tokenizer/
