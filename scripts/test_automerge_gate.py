#!/usr/bin/env python3
"""AUT-5351 + AUT-IMP-020: exercise the automerge.yml merge gates offline.

Runs the real `run:` block out of .github/workflows/automerge.yml against a stub
`gh`, so the gate logic is verified without opening PRs or spending approvals.
Standard library only.

Usage: python3 scripts/test_automerge_gate.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "automerge.yml")
REPO = "CannonFodder151/autobrainservice-website"
HEAD_SHA = "0f26af91026dc4b1a2f5e6c0b1d2a3f4c5d6e7f8"
OPEN_RUN = "aaaabbbb-cccc-dddd-eeee-ffff00001111"
CODE_RUN = "bbbbcccc-dddd-eeee-ffff-000011112222"
CRITICAL_RUN = "ccccdddd-eeee-ffff-0000-111122223333"

STUB_GH = '''#!/usr/bin/env python3
import json, os, subprocess, sys
fix = json.loads(os.environ["GH_STUB_FIXTURE"])
argv = sys.argv[1:]
if argv[:2] == ["pr", "merge"]:
    with open(os.environ["GH_STUB_MERGE_LOG"], "a") as fh:
        fh.write("\\t".join(argv) + "\\n")
    sys.exit(0)
url = next((a for a in argv[1:] if not a.startswith("-")), "")
payload = {"default_branch": "main"}
if url.endswith("/compare/main..." + fix["head_sha"]):
    payload = {"status": fix["status"], "ahead_by": fix["ahead_by"], "behind_by": fix["behind_by"]}
elif "/issues/%s/comments" % fix["pr"] in url:
    comments = []
    if fix.get("code_marker"):
        comments.append({
            "user": {"login": fix.get("code_marker_user", fix["owner"])},
            "body": f'<!-- paperclip-approve-code-reviewer: {fix["issue"]} run: {fix["code_marker"]} -->'
        })
    if fix.get("critical_marker"):
        comments.append({
            "user": {"login": fix.get("critical_marker_user", fix["owner"])},
            "body": f'<!-- paperclip-approve-critical-reviewer: {fix["issue"]} run: {fix["critical_marker"]} -->'
        })
    payload = comments
elif url.endswith("/pulls/%s" % fix["pr"]):
    body = ""
    if fix.get("open_run"):
        body = f"<!-- paperclip-run: {fix['open_run']} -->"
    checks = [{"conclusion": "SUCCESS"}]
    if fix.get("checks_green") is False:
        checks = [{"conclusion": "FAILURE"}]
    labels = [{"name": l} for l in fix.get("labels", [])]
    payload = {
        "base": {"ref": "main"},
        "draft": fix.get("draft", False),
        "mergeable_state": fix.get("mergeable_state", "clean"),
        "head": {"sha": fix["head_sha"]},
        "user": {"login": fix["author"]},
        "labels": labels,
        "statusCheckRollup": checks,
        "body": body,
    }
if fix.get("empty_compare") and "/compare/" in url:
    sys.exit(1)
out = json.dumps(payload)
if "--jq" in argv:
    jq_expr = argv[argv.index("--jq") + 1]
    jq_argv = ["jq", "-r"]
    for i, a in enumerate(argv):
        if a == "--arg":
            jq_argv += ["--arg", argv[i + 1], argv[i + 2]]
    jq_argv.append(jq_expr)
    res = subprocess.run(jq_argv, input=out, text=True, capture_output=True)
    print(res.stdout, end="")
    sys.exit(res.returncode)
print(out)
'''

# Test cases: (name, fixture_modifications, expect_merge, expect_log_substring)
# Base fixture provides a normal PR on current main with green checks
BASE_FIXTURE = {
    "pr": 42,
    "head_sha": HEAD_SHA,
    "status": "ahead",
    "ahead_by": 3,
    "behind_by": 0,
    "empty_compare": False,
    "owner": "CannonFodder151",
    "author": "CannonFodder151",
    "issue": "AUT-1234",
    "open_run": OPEN_RUN,
    "code_marker": CODE_RUN,
    "critical_marker": CRITICAL_RUN,
    "labels": [],
}

CASES = [
    # Base gate tests (from AUT-5351)
    ("orphan head with no merge-base", {"status": "diverged", "ahead_by": 1, "behind_by": 2}, False, "not based on current main"),
    ("divergent, ahead_by > 0", {"status": "diverged", "ahead_by": 7, "behind_by": 2}, False, "not based on current main"),
    ("head is behind main", {"status": "behind", "ahead_by": 0, "behind_by": 5}, False, "not based on current main"),
    ("head identical to main", {"status": "identical", "ahead_by": 0, "behind_by": 0}, False, "not based on current main"),
    ("compare API unavailable", {"empty_compare": True}, False, "not based on current main"),
    ("draft PR", {"draft": True}, False, "skip: draft PR"),
    ("dirty mergeable_state", {"mergeable_state": "dirty"}, False, "mergeable_state=dirty"),
    ("hold label", {"labels": ["hold"]}, False, "hold"),
    ("status checks not green", {"checks_green": False}, False, "status checks not green"),

    # Dual sign-off tests (AUT-IMP-020)
    ("normal PR: both approvals present", {}, True, None),
    ("missing code-reviewer approval", {"code_marker": None}, False, "no paperclip-approve-code-reviewer marker"),
    ("missing critical-reviewer approval", {"critical_marker": None}, False, "no paperclip-approve-critical-reviewer marker"),
    ("code-reviewer same as opening run", {"code_marker": OPEN_RUN}, False, "code-reviewer approval marker is from the same Paperclip run that opened the PR"),
    ("critical-reviewer same as opening run", {"critical_marker": OPEN_RUN}, False, "critical-reviewer approval marker is from the same Paperclip run that opened the PR"),
    ("both approvals from same run", {"code_marker": "dddddddd-eeee-ffff-0000-111122223333", "critical_marker": "dddddddd-eeee-ffff-0000-111122223333"}, False, "both approvals from the same Paperclip run"),
    ("no opening run stamp", {"open_run": None}, False, "PR body carries no paperclip-run stamp"),
    ("code marker from non-owner", {"code_marker": CODE_RUN, "code_marker_user": "random-user"}, False, "no paperclip-approve-code-reviewer marker"),
]

def gate_script():
    lines = open(WORKFLOW, encoding="utf-8").read().splitlines()
    step = next(i for i, l in enumerate(lines) if "Squash-merge approved PR" in l)
    start = next(i for i, l in enumerate(lines[step:], step) if l.strip() == "run: |")
    body = []
    indent = None
    for line in lines[start + 1:]:
        pad = len(line) - len(line.lstrip())
        if line.strip():
            if indent is None:
                indent = pad
            elif pad < indent:
                break
        body.append(line)
    script = textwrap.dedent("\n".join(body))
    for expr, val in (
        ("github.repository", REPO),
        ("steps.pr.outputs.pr", "42"),
        ("secrets.GITHUB_TOKEN", "stub"),
    ):
        script = script.replace("${{ %s }}" % expr, val)
    assert "${{" not in script, "unsubstituted Actions expression in extracted script"
    return script


def run_case(tmp, name, overrides, expect_merge, expect_log):
    merge_log = os.path.join(tmp, "merge.log")
    open(merge_log, "w").close()
    bindir = os.path.join(tmp, "bin")
    os.makedirs(bindir, exist_ok=True)
    stub = os.path.join(bindir, "gh")
    with open(stub, "w") as fh:
        fh.write(STUB_GH)
    os.chmod(stub, 0o755)

    fixture = BASE_FIXTURE.copy()
    fixture.update(overrides)

    # Handle special overrides
    if fixture.get("draft"):
        fixture["draft"] = True
    if fixture.get("mergeable_state"):
        pass  # handled in PR payload below
    if fixture.get("checks_green") is False:
        fixture["checks_green"] = False
    if fixture.get("code_marker_user"):
        # This would require modifying the stub; for now we test owner check by
        # setting code_marker to a value but having the stub return empty for non-owner
        # Simpler: just omit the marker (treated as missing)
        pass

    env = dict(os.environ, PATH=bindir + os.pathsep + os.environ["PATH"],
               GH_STUB_FIXTURE=json.dumps(fixture), GH_STUB_MERGE_LOG=merge_log)
    proc = subprocess.run(["bash", "-c", gate_script()], env=env,
                          capture_output=True, text=True)
    merged = open(merge_log).read()
    ok = (expect_merge == bool(merged)) and (not expect_merge or (HEAD_SHA in merged and "--squash" in merged))
    if expect_log:
        ok = ok and expect_log in proc.stdout
    print("%s %s" % ("PASS" if ok else "FAIL", name))
    if not ok:
        print("  merge log: %r" % merged)
        print("  stdout: %s" % proc.stdout)
        print("  stderr: %s" % proc.stderr)
    return ok


def main():
    with tempfile.TemporaryDirectory() as tmp:
        results = [run_case(tmp, *case) for case in CASES]
    print("\n%d/%d gates behaved as expected" % (sum(results), len(results)))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())