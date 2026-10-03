#!/usr/bin/env python3
"""AUT-5351: exercise the automerge.yml merge gates offline.

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
elif url.endswith("/pulls/%s/reviews" % fix["pr"]):
    payload = [{"user": {"login": "qa-reviewer"}, "state": "APPROVED"}]
elif url.endswith("/pulls/%s" % fix["pr"]):
    payload = {
        "base": {"ref": "main"},
        "draft": False,
        "mergeable_state": "clean",
        "head": {"sha": fix["head_sha"]},
        "user": {"login": "CannonFodder151"},
        "labels": [],
        "statusCheckRollup": [{"conclusion": "SUCCESS"}],
    }
if fix["empty_compare"] and "/compare/" in url:
    sys.exit(1)  # compare API failure: must fail closed, never fall through
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

# status / ahead_by / behind_by as returned by GET /repos/{repo}/compare/{base}...{head}
CASES = [
    ("orphan head with no merge-base", "diverged", 1, 2, False, False, "not based on current main"),
    ("divergent, ahead_by > 0 (PR #158 shape)", "diverged", 7, 2, False, False, "not based on current main"),
    ("head is behind main", "behind", 0, 5, False, False, "not based on current main"),
    ("head identical to main", "identical", 0, 0, False, False, "not based on current main"),
    ("compare API unavailable", None, 0, 0, True, False, "not based on current main"),
    ("normal PR on current main", "ahead", 3, 0, False, True, None),
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


def run_case(tmp, name, status, ahead, behind, empty_compare, expect_merge, expect_log):
    merge_log = os.path.join(tmp, "merge.log")
    open(merge_log, "w").close()
    bindir = os.path.join(tmp, "bin")
    os.makedirs(bindir, exist_ok=True)
    stub = os.path.join(bindir, "gh")
    with open(stub, "w") as fh:
        fh.write(STUB_GH)
    os.chmod(stub, 0o755)
    fixture = json.dumps({"pr": 42, "head_sha": HEAD_SHA, "status": status,
                          "ahead_by": ahead, "behind_by": behind,
                          "empty_compare": empty_compare})
    env = dict(os.environ, PATH=bindir + os.pathsep + os.environ["PATH"],
               GH_STUB_FIXTURE=fixture, GH_STUB_MERGE_LOG=merge_log)
    proc = subprocess.run(["bash", "-c", gate_script()], env=env,
                          capture_output=True, text=True)
    merged = open(merge_log).read()
    ok = (expect_merge == bool(merged)) and (not expect_merge or (HEAD_SHA in merged and "--squash" in merged))
    if expect_log:
        ok = ok and expect_log in proc.stdout
    print("%s %s" % ("PASS" if ok else "FAIL", name))
    if not ok:
        print("  merge log: %r\n  stdout: %s\n  stderr: %s" % (merged, proc.stdout, proc.stderr))
    return ok


def main():
    cases = [(c[0], *c[1:]) for c in CASES]
    with tempfile.TemporaryDirectory() as tmp:
        results = [run_case(tmp, *case) for case in cases]
    print("\n%d/%d gates behaved as expected" % (sum(results), len(results)))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())