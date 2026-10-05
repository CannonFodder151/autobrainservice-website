#!/usr/bin/env python3
"""Tests: no PR-reachable workflow job may target a self-hosted runner (AUT-5635).

A `pull_request` event checks out the PR's merge ref, so every step in such a
job runs contributor-authored code. On a self-hosted runner that is
root-equivalent on an internal box holding infra credentials -- the "pwn
requests" class (GHSA-8x5q-6f9x, GHSA-4r62-v4vq-8hh6). `seo-drift.yml` shipped
`runs-on: [self-hosted, linux, x64, vm2]` with exactly that reach: green on
2026-10-04 four times. AUT-3718 had already moved the other workflows off that
runner and missed this one.

This walks .github/workflows/*.y*ml and fails if a file whose `on:` block
triggers on pull_request names a self-hosted runner in any `runs-on:`. The scan
is a stdlib line scan on purpose -- no YAML dependency, so it cannot be defeated
by a shape a parser reads differently than the runner does.

Run: python3 scripts/test_workflow_runner_isolation.py
"""
import re
import unittest
from pathlib import Path

WORKFLOW_DIR = Path(__file__).resolve().parent.parent / ".github" / "workflows"

TOP_LEVEL_KEY = re.compile(r"^(?:[\"']?)([A-Za-z_][\w.-]*)(?:[\"']?)\s*:")
PULL_REQUEST_KEY = re.compile(r"^\s*pull_request")
RUNS_ON = re.compile(r"^\s*runs-on\s*:\s*(.*)$")
SELF_HOSTED = "self-hosted"


def workflow_files():
    if not WORKFLOW_DIR.is_dir():
        return []
    return sorted(p for p in WORKFLOW_DIR.iterdir()
                  if p.suffix in (".yml", ".yaml"))


def triggers_on_pull_request(lines):
    """True if the top-level `on:` block names a pull_request key.

    Prefix-matched rather than matched to the full key on purpose:
    `pull_request_target` runs PR code too, and `pull_request_review` is
    close enough that treating it as PR-reachable only risks failing closed.
    """
    in_on_block = False
    on_indent = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if not in_on_block:
            key = TOP_LEVEL_KEY.match(line)
            if key and indent <= 0 and key.group(1) == "on":
                in_on_block, on_indent = True, indent
            continue
        if indent <= on_indent and TOP_LEVEL_KEY.match(line):
            break
        if PULL_REQUEST_KEY.match(line):
            return True
    return False


def self_hosted_runs_on(lines):
    """(lineno, value) for every self-hosted `runs-on` in the file.

    Handles the three shapes a runs-on takes in practice: inline scalar,
    flow sequence (`[self-hosted, linux, ...]`) and block sequence.
    """
    hits = []
    in_block = False
    block_indent = 0
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if in_block:
            if indent > block_indent and stripped.startswith("-"):
                if SELF_HOSTED in stripped:
                    hits.append((lineno, stripped))
                continue
            in_block = False
        match = RUNS_ON.match(line)
        if not match:
            continue
        value = match.group(1).strip()
        if SELF_HOSTED in value:
            hits.append((lineno, value))
        elif not value:
            in_block, block_indent = True, indent
    return hits


class TestScanner(unittest.TestCase):
    """The scanner itself, pinned to the workflow shape that actually shipped.

    Regression tests age badly: once the fix merges, seo-drift.yml no longer
    proves this guard can fail. These fixtures keep that property permanent.
    """

    OLD_SEO_DRIFT = """name: SEO Drift Check

on:
  pull_request:
    paths:
      - "**/*.html"
      - "scripts/check_seo_*.py"
  schedule:
    - cron: "0 6 * * 1"
  workflow_dispatch:

jobs:
  check:
    runs-on: [self-hosted, linux, x64, vm2]
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
      - run: python3 scripts/check_seo_drift.py
"""

    def test_flags_the_pre_fix_seo_drift_workflow(self):
        lines = self.OLD_SEO_DRIFT.splitlines()
        self.assertTrue(triggers_on_pull_request(lines))
        self.assertEqual(["[self-hosted, linux, x64, vm2]"],
                         [v for _, v in self_hosted_runs_on(lines)])

    def test_clean_workflow_is_not_flagged(self):
        lines = self.OLD_SEO_DRIFT.replace(
            "runs-on: [self-hosted, linux, x64, vm2]",
            "runs-on: ubuntu-latest").splitlines()
        self.assertEqual([], self_hosted_runs_on(lines))

    def test_block_sequence_form_is_flagged(self):
        lines = ["on:", "  pull_request:", "jobs:", "  check:", "    runs-on:",
                 "      - self-hosted", "      - linux", "      - x64"]
        self.assertTrue(triggers_on_pull_request(lines))
        self.assertEqual(["- self-hosted"],
                         [v for _, v in self_hosted_runs_on(lines)])

    def test_pull_request_target_counts_as_pr_reachable(self):
        lines = ["on:", "  pull_request_target:", "jobs:", "  check:",
                 "    runs-on: [self-hosted, linux]", "    steps: []"]
        self.assertTrue(triggers_on_pull_request(lines))
        self.assertEqual(["[self-hosted, linux]"],
                         [v for _, v in self_hosted_runs_on(lines)])

    def test_schedule_only_workflow_is_out_of_scope(self):
        # N-3 closes the PR-reachable path only. A self-hosted job on a
        # schedule runs no contributor code, so it must not fail this guard.
        lines = ["on:", "  schedule:", "    - cron: '0 4 * * *'", "jobs:",
                 "  hygiene:", "    runs-on: [self-hosted, linux]"]
        self.assertFalse(triggers_on_pull_request(lines))

    def test_on_block_stops_at_the_next_top_level_key(self):
        # Otherwise a pull_request: anywhere below `on:` -- a step, a comment,
        # a job-level condition -- would count as a trigger.
        lines = ["on:", "  schedule:", "    - cron: '0 4 * * *'", "env:",
                 "  DOC: see pull_request docs", "jobs:", "  check:",
                 "    runs-on: [self-hosted, linux]"]
        self.assertFalse(triggers_on_pull_request(lines))


class TestRepositoryWorkflows(unittest.TestCase):
    def test_no_pull_request_workflow_uses_a_self_hosted_runner(self):
        offenders = []
        for path in workflow_files():
            lines = path.read_text(encoding="utf-8").splitlines()
            if not triggers_on_pull_request(lines):
                continue
            rel = path.relative_to(WORKFLOW_DIR.parent.parent)
            offenders += [f"{rel}:{lineno}: {value}"
                          for lineno, value in self_hosted_runs_on(lines)]
        self.assertEqual(
            [], offenders,
            "a pull_request-triggered workflow must not run on a self-hosted "
            "runner -- move the job to ubuntu-latest (AUT-5635)")

    def test_the_scan_is_not_vacuous(self):
        # Guards the guard: a wrong WORKFLOW_DIR or a broken trigger regex
        # would make the test above pass without checking anything.
        files = workflow_files()
        self.assertTrue(files, f"no workflow files found under {WORKFLOW_DIR}")
        reachable = [p.name for p in files
                     if triggers_on_pull_request(p.read_text(encoding="utf-8")
                                                .splitlines())]
        self.assertTrue(reachable,
                        "no workflow reads as pull_request-reachable, so the "
                        "runner-isolation scan never checks anything")


if __name__ == "__main__":
    unittest.main(verbosity=2)