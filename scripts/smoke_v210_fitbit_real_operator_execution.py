"""Retired compatibility entry point for the legacy Fitbit Web API smoke."""
from __future__ import annotations
import argparse

SCRIPT_NAME = "v210-fitbit-real-operator-execution"

def main() -> int:
    parser = argparse.ArgumentParser(description="Legacy Fitbit Web API execution is retired.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--allow-real-request", action="store_true")
    parser.parse_args()
    print(f"[{SCRIPT_NAME}] ERROR: legacy Fitbit Web API execution is retired; use Google Health API")
    print("v210_fitbit_real_operator_execution_network_request: False")
    print("v210_fitbit_real_operator_execution_real_operator_execution: False")
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
