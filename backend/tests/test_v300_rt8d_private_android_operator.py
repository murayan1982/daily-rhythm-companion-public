"""Credential-free tests for RT-8d private Android operator tooling."""
from __future__ import annotations
import io, json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[2]; SCRIPTS=ROOT/"scripts"
if str(SCRIPTS) not in sys.path: sys.path.insert(0,str(SCRIPTS))
import run_v300_rt8d_private_android_operator as runner
import validate_v300_rt8_private_operator_manifest as validator
ANDROID_HEAD="d"*40
class FakeGit:
    def __init__(self, head=ANDROID_HEAD, status="", ancestor=True): self.head=head; self.status=status; self.ancestor=ancestor
    def output(self,args,root):
        del root
        return {("branch","--show-current"):"main",("rev-parse","HEAD"):self.head,
            ("rev-parse","origin/main"):self.head,("status","--porcelain"):self.status,
            ("ls-files","--cached","--",runner.MANIFEST_RELATIVE.as_posix()):""}[args]
    def ok(self,args,root): del root; return self.ancestor if args[0]=="merge-base" else args[0] in {"cat-file","check-ignore"}
def good(root,ok,out): del root,ok,out; return runner.TargetState(True,True,False,False)
def confirmations(): return io.StringIO("\n".join(runner.EXPECTED_CONFIRMATIONS)+"\n")
def write_pc(root,pc=runner.PC_ACCEPTED_SOURCE_HEAD):
    t=root/runner.MANIFEST_RELATIVE; t.parent.mkdir(parents=True,exist_ok=True)
    d=validator.expected_manifest_for_stage("pc_windows",pc_head=pc); t.write_text(json.dumps(d)+"\n",encoding="utf-8"); return d
def test_inert_mode_performs_no_access_write_or_execution(tmp_path):
    o=io.StringIO(); assert runner.run_operator(mode="check_inert",root=tmp_path,stdout=o,stderr=io.StringIO())==0; assert "private_manifest_read: False" in o.getvalue()
def test_clean_source_preflight_passes(tmp_path):
    f=FakeGit(); assert runner.preflight(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=good)==ANDROID_HEAD
def test_wrong_expected_head_is_rejected(tmp_path):
    f=FakeGit();
    with pytest.raises(runner.OperatorError) as e: runner.preflight("e"*40,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=good)
    assert e.value.code=="expected_source_head_mismatch"
def test_dirty_tree_is_rejected(tmp_path):
    f=FakeGit(status=" M README.md")
    with pytest.raises(runner.OperatorError) as e: runner.preflight(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=good)
    assert e.value.code=="working_tree_not_clean"
def test_rt8c_acceptance_ancestry_is_required(tmp_path):
    f=FakeGit(ancestor=False)
    with pytest.raises(runner.OperatorError): runner.preflight(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=good)
def test_missing_manifest_is_rejected(tmp_path):
    f=FakeGit(); state=lambda r,o,g: runner.TargetState(True,False,False,False)
    with pytest.raises(runner.OperatorError) as e: runner.preflight(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=state)
    assert e.value.code=="target_missing"
def test_nonignored_manifest_is_rejected(tmp_path):
    f=FakeGit(); state=lambda r,o,g: runner.TargetState(False,True,False,False)
    with pytest.raises(runner.OperatorError) as e: runner.preflight(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=state)
    assert e.value.code=="target_not_ignored"
def test_symlink_or_nonregular_manifest_is_rejected(tmp_path):
    f=FakeGit(); state=lambda r,o,g: runner.TargetState(True,True,True,False)
    with pytest.raises(runner.OperatorError) as e: runner.preflight(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=state)
    assert e.value.code=="target_is_symlink"
def test_valid_pc_transition_check_passes(tmp_path):
    write_pc(tmp_path); f=FakeGit(); h,raw,d=runner._load_pc_transition(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=good); assert h==ANDROID_HEAD and raw and d["stage"]=="pc_windows"
def test_wrong_previous_stage_is_rejected(tmp_path):
    t=tmp_path/runner.MANIFEST_RELATIVE; t.parent.mkdir(parents=True); d=validator.expected_manifest_for_stage("android",pc_head=runner.PC_ACCEPTED_SOURCE_HEAD,android_head=ANDROID_HEAD); t.write_text(json.dumps(d))
    f=FakeGit();
    with pytest.raises(runner.OperatorError) as e: runner._load_pc_transition(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=good)
    assert e.value.code=="pc_transition_manifest_invalid"
def test_wrong_pc_candidate_source_is_rejected(tmp_path):
    write_pc(tmp_path,"c"*40); f=FakeGit()
    with pytest.raises(runner.OperatorError) as e: runner._load_pc_transition(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=good)
    assert e.value.code=="pc_candidate_source_mismatch"
def test_nonancestor_pc_source_is_rejected(tmp_path):
    write_pc(tmp_path); f=FakeGit(ancestor=False)
    with pytest.raises(runner.OperatorError): runner._load_pc_transition(ANDROID_HEAD,root=tmp_path,git_output=f.output,git_ok=f.ok,target_probe=good)
def test_wrong_confirmation_creates_no_update(tmp_path):
    write_pc(tmp_path); t=tmp_path/runner.MANIFEST_RELATIVE; before=t.read_bytes(); f=FakeGit(); c=runner.run_operator(mode="record_android",expected_source_head=ANDROID_HEAD,root=tmp_path,stdin=io.StringIO("WRONG\n"),stdout=io.StringIO(),stderr=io.StringIO(),git_output=f.output,git_ok=f.ok,target_probe=good); assert c==3 and t.read_bytes()==before
def test_successful_transition_creates_exact_android_manifest(tmp_path):
    write_pc(tmp_path); f=FakeGit(); assert runner.run_operator(mode="record_android",expected_source_head=ANDROID_HEAD,root=tmp_path,stdin=confirmations(),stdout=io.StringIO(),stderr=io.StringIO(),git_output=f.output,git_ok=f.ok,target_probe=good)==0; a=json.loads((tmp_path/runner.MANIFEST_RELATIVE).read_text()); assert a==validator.expected_manifest_for_stage("android",pc_head=runner.PC_ACCEPTED_SOURCE_HEAD,android_head=ANDROID_HEAD)
def test_accepted_pc_section_remains_structurally_equal(tmp_path):
    old=write_pc(tmp_path); f=FakeGit(); runner.run_operator(mode="record_android",expected_source_head=ANDROID_HEAD,root=tmp_path,stdin=confirmations(),stdout=io.StringIO(),stderr=io.StringIO(),git_output=f.output,git_ok=f.ok,target_probe=good); new=json.loads((tmp_path/runner.MANIFEST_RELATIVE).read_text()); assert new["pc_windows"]==old["pc_windows"]
def test_android_candidate_becomes_current_source_head(tmp_path):
    write_pc(tmp_path); f=FakeGit(); runner.run_operator(mode="record_android",expected_source_head=ANDROID_HEAD,root=tmp_path,stdin=confirmations(),stdout=io.StringIO(),stderr=io.StringIO(),git_output=f.output,git_ok=f.ok,target_probe=good); a=json.loads((tmp_path/runner.MANIFEST_RELATIVE).read_text()); assert a["android_candidate_source_head"]==ANDROID_HEAD
def test_atomic_replacement_failure_preserves_original_and_removes_temp(tmp_path):
    write_pc(tmp_path); t=tmp_path/runner.MANIFEST_RELATIVE; before=t.read_bytes(); f=FakeGit()
    def fail(s,d): raise OSError("synthetic")
    c=runner.run_operator(mode="record_android",expected_source_head=ANDROID_HEAD,root=tmp_path,stdin=confirmations(),stdout=io.StringIO(),stderr=io.StringIO(),git_output=f.output,git_ok=f.ok,target_probe=good,replace_func=fail); assert c==3 and t.read_bytes()==before and not t.with_name(t.name+".rt8d-transition.tmp").exists()
def test_output_never_echoes_private_path_content_token_or_operator_input(tmp_path):
    write_pc(tmp_path); f=FakeGit(); secret=r"C:\\Users\\private\\secret-token-value"; o,e=io.StringIO(),io.StringIO(); c=runner.run_operator(mode="record_android",expected_source_head=ANDROID_HEAD,root=tmp_path,stdin=io.StringIO(secret+"\n"),stdout=o,stderr=e,git_output=f.output,git_ok=f.ok,target_probe=good); rendered=o.getvalue()+e.getvalue(); assert c==3 and secret not in rendered and str(tmp_path) not in rendered and "schema_version" not in rendered and "operator_evidence" not in rendered
