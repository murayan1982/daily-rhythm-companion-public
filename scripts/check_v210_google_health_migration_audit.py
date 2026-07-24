"""Source-tree guard for W-5b1 Google Health API migration correction."""
from __future__ import annotations
from pathlib import Path
import subprocess, sys

ROOT=Path(__file__).resolve().parents[1]

def read(rel:str)->str:
    p=ROOT/rel
    if not p.exists(): raise AssertionError(f"Missing required file: {rel}")
    return p.read_text(encoding="utf-8")

def require(text:str, fragment:str, label:str)->None:
    if fragment not in text: raise AssertionError(f"Missing {label}: {fragment}")

def main()->None:
    config=read("backend/app/config.py")
    source=read("backend/app/services/google_health_sleep_source.py")
    parser=read("backend/app/services/google_health_sleep_parser.py")
    selection=read("backend/app/services/sleep_provider_selection_service.py")
    flutter=read("app/lib/models/sleep_provider_selection.dart")
    home=read("app/lib/screens/home_screen.dart")
    runner=read("backend/scripts/run_fitbit_real_operator.ps1")
    execution=read("scripts/smoke_v210_fitbit_real_operator_execution.py")
    doc=read("docs/v210_google_health_migration_audit.md")
    checklist=read("docs/DRC_v210_goal_checklist_small_commit.md")
    for text, fragment in [
        (config,'https://health.googleapis.com/v4'),
        (config,'/users/me/dataTypes/sleep/dataPoints'),
        (config,'googlehealth.sleep.readonly'),
        (source,'sleep.interval.civil_end_time'),
        (parser,'minutesAsleep'),
        (parser,'stagesSummary'),
        (selection,'legacy_migration_reference'),
        (flutter,"json['provider_options']"),
        (home,'新しい実利用経路にはGoogle Health'),
        (runner,'Legacy Fitbit Web API execution is retired'),
        (execution,'legacy Fitbit Web API execution is retired'),
        (doc,'September 2026'),
        (checklist,'Current small commit: C-1a'),
        (checklist,'W-5b1  COMPLETED / ACCEPTED'),
        (doc,'Status: COMPLETED / ACCEPTED'),
        (doc,'implementation commit: 081cfdd'),
        (checklist,'W-5b2  COMPLETED / ACCEPTED'),
    ]: require(text,fragment,"migration audit contract")
    proc=subprocess.run([sys.executable,'-m','pytest','-q','backend/tests/test_google_health_v4_migration_contract.py'],cwd=ROOT,capture_output=True,text=True,check=False)
    if proc.returncode!=0: raise AssertionError(proc.stdout+proc.stderr)
    denied=subprocess.run([sys.executable,'scripts/smoke_v210_fitbit_real_operator_execution.py','--allow-real-request'],cwd=ROOT,capture_output=True,text=True,check=False)
    if denied.returncode==0: raise AssertionError('Legacy Fitbit execution was not blocked')
    require(denied.stdout,'network_request: False','legacy execution network denial')
    print('v210_google_health_migration_audit_status: completed-accepted')
    print('v210_google_health_migration_audit_completed_small_commit: W-5b1')
    print('v210_google_health_migration_audit_current_small_commit: C-1a')
    print('v210_google_health_migration_audit_parent_phase: W-5-completed-accepted')
    print('v210_google_health_migration_audit_legacy_fitbit_execution: retired')
    print('v210_google_health_migration_audit_real_operator_execution: accepted-in-W-5b2')
    print('v210_google_health_migration_audit_w5b2_completed_accepted: True')
    print('v210_google_health_migration_audit_release_records_changed: false')
    print('[v210-google-health-migration-audit-check] OK')

if __name__=='__main__': main()
