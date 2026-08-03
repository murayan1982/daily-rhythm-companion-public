#!/usr/bin/env python3
"""Credential-free RT-8d Stage 1 exact-source verification gate."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
BASELINE="b889ce884a928809125c473dcd2e8cd7a4c020ef"; PARENT="fa39065130a4a4689c2e54195f231a5e79c62a35"
MESSAGE="docs/test: sync RT-8c PC Windows acceptance"; PC=PARENT; SCHEMA="drc.v3.rt8-platform-acceptance.2"
MREL="operator_evidence/v300_rt8_pc_android_realtime_acceptance.json"; MANIFEST=ROOT/MREL
BASE_PATHS={"README.md","roadmap.md","tasklist.md","scripts/README.md","docs/DRC_v300_goal_checklist_small_commit.md","docs/v300_rt8c_configured_pc_windows_realtime_acceptance.md","scripts/check_v300_rt8c_configured_pc_windows_realtime_acceptance.py"}
EXACT={"README.md","roadmap.md","tasklist.md","scripts/README.md","docs/DRC_v300_goal_checklist_small_commit.md","docs/v300_rt8d_configured_android_realtime_acceptance.md","scripts/check_v300_rt8d_configured_android_realtime_acceptance.py","scripts/run_v300_rt8d_private_android_operator.py","backend/tests/test_v300_rt8d_private_android_operator.py"}
TOP=("README.md","roadmap.md","tasklist.md","scripts/README.md","docs/DRC_v300_goal_checklist_small_commit.md")
def fail(m): raise SystemExit("v300_rt8d_stage1_gate_error: "+m)
def req(c,m):
    if not c: fail(m)
def git(*a): return subprocess.run(["git",*a],cwd=ROOT,check=True,text=True,encoding="utf-8",errors="surrogateescape",stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout.strip()
def paths(s): return {x.replace("\\","/") for x in s.splitlines() if x}
def changed(): return paths(git("diff","--name-only"))|paths(git("diff","--cached","--name-only"))|paths(git("ls-files","--others","--exclude-standard"))
def read(p):
    q=ROOT/p; req(q.is_file(),"missing "+p); return q.read_text(encoding="utf-8")
def main():
    req(git("rev-parse","HEAD")==BASELINE,"HEAD mismatch"); req(git("rev-parse","origin/main")==BASELINE,"origin mismatch")
    req(git("rev-parse",BASELINE+"^")==PARENT,"parent mismatch"); req(git("show","-s","--format=%s",BASELINE)==MESSAGE,"message mismatch")
    req(paths(git("diff-tree","--no-commit-id","--name-only","-r",BASELINE))==BASE_PATHS,"baseline surface mismatch")
    req(changed()==EXACT,"exact Stage 1 surface mismatch")
    for p in TOP:
        t=read(p)
        for m in ("RT-8d Stage 1","IMPLEMENTED / AWAITING_REVIEW",BASELINE,"exact 9 files","RT-8d Stage 2","NOT_AUTHORIZED"): req(m in t,f"{p} missing {m}")
    c=read("docs/v300_rt8d_configured_android_realtime_acceptance.md")
    for m in ("A -> B -> C -> D -> E -> F -> G -> H","natural_voice_turn_count: 1","confirmed_user_speech_event_count: 1","drc_local_interruption_count: 1","recovery_voice_turn_count: 1","manual_vts_apply_count: 1","private manifest read: false","Android execution: false","exactly eighteen credential-free tests"): req(m in c,"contract missing "+m)
    r=read("scripts/run_v300_rt8d_private_android_operator.py")
    for m in ("--check-inert","--preflight","--check-pc-transition","--record-android","PASS-ANDROID-","ACCEPT-ANDROID","expected_manifest_for_stage","pc_candidate_source_mismatch","os.replace"): req(m in r,"runner missing "+m)
    low=r.lower()
    for f in ("import requests","import httpx","import socket","import adb","import pyvts","import websockets","popen(","start-process"): req(f not in low,"runner forbidden "+f)
    tests=read("backend/tests/test_v300_rt8d_private_android_operator.py"); req(tests.count("def test_")==18,"focused test count")
    req(os.path.lexists(MANIFEST) and MANIFEST.is_file() and not MANIFEST.is_symlink(),"manifest state")
    req(subprocess.run(["git","check-ignore","--quiet","--",MREL],cwd=ROOT).returncode==0,"manifest ignored")
    req(git("ls-files","--cached","--",MREL)=="","manifest tracked")
    before=MANIFEST.stat(); cp=subprocess.run([sys.executable,"scripts/run_v300_rt8d_private_android_operator.py","--check-inert"],cwd=ROOT,check=True,text=True,encoding="utf-8",stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    req(cp.stderr=="","inert stderr")
    for m in ("private_manifest_read: False","private_manifest_modified: False","android_adb_started: False","provider_network_vts_attempted: False"): req(m in cp.stdout,"inert marker "+m)
    after=MANIFEST.stat(); req((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),"manifest metadata changed")
    print("v300_rt8d_stage1_status: operator-tooling-implemented-awaiting-review")
    print("v300_rt8d_stage1_baseline:",BASELINE); print("v300_rt8d_stage1_origin_main_verified: True")
    print("v300_rt8d_stage1_exact_change_surface: True"); print("v300_rt8d_stage1_change_file_count: 9")
    print("v300_rt8d_schema_version:",SCHEMA); print("v300_rt8d_pc_accepted_source_head:",PC)
    print("v300_rt8d_operator_runner_inert_by_default: True"); print("v300_rt8d_operator_runner_starts_processes: False")
    print("v300_rt8d_private_manifest_exists: True"); print("v300_rt8d_private_manifest_ignored: True")
    print("v300_rt8d_private_manifest_tracked: False"); print("v300_rt8d_private_manifest_read: False")
    print("v300_rt8d_private_manifest_modified: False"); print("v300_rt8d_android_execution_performed: False")
    print("v300_rt8d_backend_runtime_changed: False"); print("v300_rt8d_flutter_runtime_changed: False")
    print("v300_rt8d_existing_tests_changed: False"); print("v300_rt8d_new_focused_test_count: 18")
    print("v300_rt8d_stage2_authorized: False"); print("v300_rt8d_stage1_commit_push_authorized: False")
if __name__=="__main__": main()
