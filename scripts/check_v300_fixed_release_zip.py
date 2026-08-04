#!/usr/bin/env python3
"""RT-9c v3.0.0 one-time fixed-ZIP tooling and same-artifact verifier.

Default mode validates the exact Stage 1 source/tooling candidate without reading
private evidence or creating artifacts. ``--source-tree`` requires clean
synchronized official Public main and runs the full RT-9b gate with one explicit
ignored RT-8 aggregate manifest. ``--release-zip`` verifies one supplied ZIP
without rebuilding it and remains intended only for separately authorized RT-9d.
"""
from __future__ import annotations
import argparse, os, re, shutil, stat, subprocess, sys, tempfile, zipfile
from hashlib import sha256
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
RT9B_COMMIT="15908a548c229726287867ad89c7ce8b4b916298"
EXPECTED_BACKEND_VERSION="3.0.0"
EXPECTED_FLUTTER_VERSION="3.0.0+4"
EXPECTED_BACKEND_TESTS=417
EXPECTED_FLUTTER_TESTS=500
RELEASE_TAG="DRC_v3.0.0"
OFFICIAL_ORIGIN=re.compile(r"^(?:https://github\.com/|git@github\.com:)murayan1982/daily-rhythm-companion-public(?:\.git)?$")
ZIP_PATTERN=re.compile(r"^DailyRhythmCompanion_v3\.0\.0_\d{8}_\d{6}\.zip$")
STAGE1_SURFACE={
"README.md","roadmap.md","tasklist.md","scripts/README.md",
"docs/DRC_v300_goal_checklist_small_commit.md",
"docs/v300_rt9_release_readiness_current_behavior_inventory.md",
"docs/v300_rt9_release_readiness.md","docs/v300_release_record.md",
"release_notes/v3.0.0.md","scripts/check_v300_rt9_release_readiness.py",
"docs/v300_rt9_fixed_release_zip.md","build_v300_fixed_release_zip_from_head.ps1",
"scripts/check_v300_fixed_release_zip.py"}
REQUIRED_FILES={
"README.md","roadmap.md","tasklist.md","scripts/README.md","build_release.bat",
"build_v300_fixed_release_zip_from_head.ps1","scripts/check_release_package.py",
"scripts/check_v300_rt9_release_readiness.py","scripts/check_v300_fixed_release_zip.py",
"docs/DRC_v300_goal_checklist_small_commit.md","docs/v300_rt9_release_readiness.md",
"docs/v300_rt9_fixed_release_zip.md","docs/v300_release_record.md",
"release_notes/v3.0.0.md","backend/app/version.py","app/pubspec.yaml"}
PROTECTED={
"build_release.bat":"1e939e31187b58efe7c5987fd763dba733ff706ad864a14cf945e641a9f23c1a",
"scripts/check_release_package.py":"57d6e4a6fae67bbc2e8c9e9b5c710f4d951866ad4007606075c244c6a29d212b",
"build_v210_fixed_release_zip_from_head.ps1":"434011e1ed8680a1619db845c8eda9d462d78956ed0d1d1e734c06f18c6d2f6d",
"scripts/check_v210_fixed_release_zip.py":"3fc73ffda276b45f034a8314b6af66c0176c5f715eff7dd63b632f48624c6a2a",
"docs/v210_release_record.md":"de7e83b9cd9d21bbd61805a0a09c0039c90b7a85ce9f25512e760fd0bcb562a1",
"release_notes/v2.1.0.md":"0507586860e2e4fa057c3cf5e61b8c6f9be43453c28edc50088223bb80f6bf86"}

def die(m): raise AssertionError(m)
def read(rel,root=ROOT):
 p=root/rel
 if not p.is_file(): die("missing "+rel)
 return p.read_text(encoding="utf-8")
def normhash(path): return sha256(path.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
def filehash(path):
 h=sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def cap(cmd,cwd=ROOT):
 r=subprocess.run(cmd,cwd=cwd,text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if r.returncode: die(r.stderr.strip() or "command failed: "+" ".join(cmd))
 return r.stdout.strip()
def safe_command(cmd):
 if os.name!="nt" or Path(cmd[0]).suffix.lower() not in {".bat",".cmd"}: return cmd
 comspec=os.environ.get("COMSPEC") or shutil.which("cmd.exe")
 if not comspec: die("Windows command processor required")
 return [comspec,"/d","/s","/c",subprocess.list2cmdline(cmd)]
def run(cmd,cwd=ROOT):
 r=subprocess.run(safe_command(cmd),cwd=cwd,text=True,encoding="utf-8",errors="replace",stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 print(r.stdout,end="")
 if r.returncode: die("command failed: "+" ".join(cmd))
 return r.stdout
def git_changes():
 out=set()
 for args in (("diff","--name-only"),("diff","--cached","--name-only"),("ls-files","--others","--exclude-standard")):
  out|={x.replace("\\","/") for x in cap(["git",*args]).splitlines() if x}
 return out
def source_mode():
 if cap(["git","branch","--show-current"])!="main": die("branch must be main")
 head=cap(["git","rev-parse","HEAD"]); origin=cap(["git","rev-parse","origin/main"])
 if not OFFICIAL_ORIGIN.fullmatch(cap(["git","remote","get-url","origin"])): die("official origin required")
 changes=git_changes()
 if head==RT9B_COMMIT and origin==RT9B_COMMIT and changes==STAGE1_SURFACE: return "stage1-candidate",head
 if head==origin and not changes:
  subprocess.run(["git","merge-base","--is-ancestor",RT9B_COMMIT,head],cwd=ROOT,check=True)
  return "clean-committed",head
 die("unexpected RT-9c source state")
def markers(text,values,label):
 for v in values:
  if v not in text: die(label+" missing "+v)
def verify_static(root=ROOT,stage1=True):
 for f in REQUIRED_FILES:
  if not (root/f).is_file(): die("missing required file "+f)
 markers(read("backend/app/version.py",root),['APP_VERSION = "3.0.0"'],"backend version")
 markers(read("app/pubspec.yaml",root),["version: 3.0.0+4"],"flutter version")
 record=read("docs/v300_release_record.md",root)
 markers(record,["Status: PREPARED / NOT_RELEASED","fixed ZIP basename: NOT_BUILT","fixed ZIP builder invocation count: 0","annotated tag publication: NOT_CREATED","GitHub Release publication: NOT_CREATED"],"release record")
 notes=read("release_notes/v3.0.0.md",root)
 markers(notes,["Status: RELEASE CANDIDATE / NOT_RELEASED","Fixed release ZIP: NOT_BUILT","GitHub Release: NOT_CREATED"],"release notes")
 contract=read("docs/v300_rt9_fixed_release_zip.md",root)
 if "Status: STAGE1_IMPLEMENTED / AWAITING_REVIEW" not in contract and "Status: COMPLETED / ACCEPTED" not in contract: die("tooling contract status")
 markers(contract,["builder invocation count: 0","build_v300_fixed_release_zip_from_head.ps1","scripts/check_v300_fixed_release_zip.py","## Stage 1 stop rule"],"tooling contract")
 builder=read("build_v300_fixed_release_zip_from_head.ps1",root)
 for m in ("[switch]$PreflightOnly","[string]$Rt8ManifestJson","DRC_v2.1.0","DRC_v3.0.0","DailyRhythmCompanion_v3.0.0_*.zip","scripts\\check_v300_fixed_release_zip.py","--rt8-manifest-json","git worktree add --detach","build_release.bat release","$buildInvocationCount++","verification_status: not-run","next_action: verify-this-same-zip-without-rebuilding"):
  if m not in builder: die("builder marker missing "+m)
 if "[IO.Path]::GetRelativePath" in builder: die("PowerShell 7-only API")
 for rel,digest in PROTECTED.items():
  if normhash(root/rel)!=digest: die("protected file changed "+rel)
 if stage1:
  for rel in STAGE1_SURFACE:
   text=read(rel,root)
   for pat in (r"(?i)sk-[a-z0-9_-]{12,}",r"(?i)bearer\s+[a-z0-9._~+/-]{12,}",r"(?i)\b[a-z]:\\users\\",r"\b192\.168\.\d+\.\d+\b"):
    if re.search(pat,text): die("private-looking value in "+rel)
def verify_git_clean():
 if Path(cap(["git","rev-parse","--show-toplevel"])).resolve()!=ROOT.resolve(): die("repo root mismatch")
 if cap(["git","status","--porcelain","--untracked-files=all"]): die("working tree must be clean")
 if cap(["git","branch","--show-current"])!="main": die("main required")
 if not OFFICIAL_ORIGIN.fullmatch(cap(["git","remote","get-url","origin"])): die("official origin")
 head=cap(["git","rev-parse","HEAD"]); origin=cap(["git","rev-parse","origin/main"])
 if head!=origin: die("HEAD != origin/main")
 subprocess.run(["git","merge-base","--is-ancestor",RT9B_COMMIT,head],cwd=ROOT,check=True)
 roots=[x for x in cap(["git","rev-list","--max-parents=0","HEAD"]).splitlines() if x]
 if len(roots)!=1: die("one root commit required")
 for tag in ("DRC_v2.0.0","DRC_v2.0.1","DRC_v2.1.0"):
  if cap(["git","tag","--list",tag])!=tag or cap(["git","cat-file","-t",tag])!="tag": die("annotated tag missing "+tag)
 if cap(["git","tag","--list",RELEASE_TAG]): die("v3 tag already exists")
 release=ROOT/"release"
 if release.exists() and any(release.glob("DailyRhythmCompanion_v3.0.0_*.zip")): die("v3 fixed ZIP already exists")
 return head
def flutter_path():
 names=("flutter.bat","flutter.cmd","flutter") if os.name=="nt" else ("flutter",)
 for name in names:
  p=shutil.which(name)
  if p:return p
 die("flutter required")
def parse_flutter(out):
 plain=re.sub(r"\x1b\[[0-9;?]*[ -/]*[@-~]","",out).replace("\r","\n")
 vals=re.findall(r"\+(\d+)(?:\s+-\d+)?:\s+All tests passed!",plain)
 if not vals: die("Flutter count missing")
 return int(vals[-1])
def run_extracted(root,with_flutter,with_builds):
 run([sys.executable,"-m","compileall","-q","backend","scripts"],root)
 out=run([sys.executable,"-m","pytest","-q","backend/tests"],root)
 vals=re.findall(r"(\d+) passed",out)
 if not vals or int(vals[-1])!=EXPECTED_BACKEND_TESTS: die("Backend count mismatch")
 if with_flutter:
  f=flutter_path(); run([f,"analyze"],root/"app"); out=run([f,"test"],root/"app")
  if parse_flutter(out)!=EXPECTED_FLUTTER_TESTS: die("Flutter count mismatch")
  if with_builds:
   if os.name!="nt": die("builds require Windows")
   run([f,"build","web"],root/"app"); run([f,"build","windows"],root/"app"); run([f,"build","apk","--debug"],root/"app")
def stripped(name):
 parts=PurePosixPath(name.replace("\\","/")).parts
 return "/".join(parts[1:] if parts and parts[0]=="DailyRhythmCompanion" else parts)
def verify_zip(path,expected_sha,expected_head,with_flutter,with_builds):
 if not path.is_file() or not ZIP_PATTERN.fullmatch(path.name): die("invalid v3 ZIP")
 if not re.fullmatch(r"[0-9a-f]{64}",expected_sha): die("invalid SHA")
 if not re.fullmatch(r"[0-9a-f]{40}",expected_head): die("invalid source HEAD")
 current=verify_git_clean()
 if current!=expected_head: die("expected source must equal clean current HEAD")
 checklist=read("docs/DRC_v300_goal_checklist_small_commit.md")
 if "RT-9c: COMPLETED / ACCEPTED / PUSHED" not in checklist or "RT-9d: READY_FOR_EXACT_CONTRACT_REVIEW / NOT_AUTHORIZED" not in checklist: die("RT-9d not authorized entry state")
 before_stat=path.stat(); before=filehash(path)
 if before!=expected_sha: die("ZIP SHA mismatch")
 run([sys.executable,"scripts/check_release_package.py",str(path)])
 with zipfile.ZipFile(path) as z:
  bad=z.testzip()
  if bad: die("ZIP CRC failed "+bad)
  names=[]; folded=set()
  for info in z.infolist():
   n=info.filename.replace("\\","/"); pure=PurePosixPath(n)
   if pure.is_absolute() or ".." in pure.parts: die("unsafe member "+n)
   key=n.casefold()
   if key in folded: die("duplicate/case collision "+n)
   folded.add(key); names.append(n)
   mode=(info.external_attr>>16)&0xFFFF
   if stat.S_ISLNK(mode): die("symlink member "+n)
  roots={PurePosixPath(n).parts[0] for n in names if n.strip("/")}
  if roots!={"DailyRhythmCompanion"}: die("single package root required")
  files={stripped(n) for n in names if n and not n.endswith("/")}
  missing=REQUIRED_FILES-files
  if missing: die("missing package files "+repr(sorted(missing)))
  forbidden_prefixes=("vendor/","operator_evidence/","backend/local_data/","release/",".git/","app/build/")
  for n in files:
   low=n.lower()
   if n.startswith(forbidden_prefixes) or low.endswith(".zip") or low in {".env","token.json","credentials.json"}: die("forbidden package member "+n)
  def data(rel): return z.read("DailyRhythmCompanion/"+rel)
  if b'APP_VERSION = "3.0.0"' not in data("backend/app/version.py"): die("ZIP backend version")
  if b"version: 3.0.0+4" not in data("app/pubspec.yaml"): die("ZIP flutter version")
  for rel,digest in PROTECTED.items():
   actual=sha256(data(rel).replace(b"\r\n",b"\n").replace(b"\r",b"\n")).hexdigest()
   if actual!=digest: die("ZIP protected hash "+rel)
 with tempfile.TemporaryDirectory(prefix="drc_v300_fixed_zip_") as td:
  root=Path(td)
  with zipfile.ZipFile(path) as z:
   for info in z.infolist():
    pure=PurePosixPath(info.filename.replace("\\","/")); target=root.joinpath(*pure.parts)
    if info.is_dir() or info.filename.endswith("/"): target.mkdir(parents=True,exist_ok=True)
    else:
     target.parent.mkdir(parents=True,exist_ok=True)
     with z.open(info) as src,target.open("wb") as dst: shutil.copyfileobj(src,dst)
  source=root/"DailyRhythmCompanion"; verify_static(source,stage1=False); run_extracted(source,with_flutter,with_builds)
 after_stat=path.stat(); after=filehash(path)
 if before_stat.st_size!=after_stat.st_size or before_stat.st_mtime_ns!=after_stat.st_mtime_ns or before!=after: die("ZIP changed during verification")
 return before,before_stat.st_size

def args():
 p=argparse.ArgumentParser(); p.add_argument("--source-tree",action="store_true"); p.add_argument("--release-zip",type=Path); p.add_argument("--expected-sha256"); p.add_argument("--expected-source-head"); p.add_argument("--with-flutter",action="store_true"); p.add_argument("--with-builds",action="store_true"); p.add_argument("--rt8-manifest-json",type=Path); return p.parse_args()
def main():
 a=args()
 if a.with_builds and not a.with_flutter: die("--with-builds requires --with-flutter")
 if a.with_builds and os.name!="nt": die("--with-builds requires Windows")
 if a.source_tree and a.rt8_manifest_json is None: die("--source-tree requires --rt8-manifest-json")
 if a.release_zip and (not a.expected_sha256 or not a.expected_source_head): die("release ZIP expected tuple required")
 mode,head=source_mode() if not a.source_tree and not a.release_zip else ("not-run","not-run")
 verify_static()
 source_verified=False; manifest_read=False; zip_sha="not-run"; zip_size="not-run"; same=False
 if a.source_tree:
  head=verify_git_clean(); cmd=[sys.executable,"scripts/check_v300_rt9_release_readiness.py","--with-flutter","--with-builds","--rt8-manifest-json",str(a.rt8_manifest_json)]; run(cmd); source_verified=True; manifest_read=True; mode="clean-committed"
 if a.release_zip:
  zip_sha,zip_size=verify_zip(a.release_zip.resolve(),a.expected_sha256,a.expected_source_head,a.with_flutter,a.with_builds); head=a.expected_source_head; same=True; mode="release-zip"
 print("v300_fixed_release_zip_tooling_status: stage1-implemented-awaiting-review")
 print("v300_fixed_release_zip_source_mode:",mode)
 print("v300_fixed_release_zip_stage1_baseline:",RT9B_COMMIT)
 print("v300_fixed_release_zip_exact_stage1_surface: True")
 print("v300_fixed_release_zip_stage1_change_file_count:",len(STAGE1_SURFACE))
 print("v300_fixed_release_zip_source_tree_verified:",source_verified)
 print("v300_fixed_release_zip_source_head:",head)
 print("v300_fixed_release_zip_private_manifest_read:",manifest_read)
 print("v300_fixed_release_zip_private_manifest_modified: False")
 print("v300_fixed_release_zip_same_artifact_verified:",same)
 print("v300_fixed_release_zip_size_bytes:",zip_size)
 print("v300_fixed_release_zip_sha256:",zip_sha)
 print("v300_fixed_release_zip_builder_invoked_by_verifier: False")
 print("v300_fixed_release_zip_builder_invocation_count: 0")
 print("v300_fixed_release_zip_built: False")
 print("v300_fixed_release_zip_tag_created: False")
 print("v300_fixed_release_zip_github_release_created: False")
 print("v300_rt9c_stage2_authorized: False")
 print("v300_rt9d_authorized: False")
 print("v300_release_ready: False")
if __name__=="__main__": main()
