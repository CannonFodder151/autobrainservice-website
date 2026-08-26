#!/usr/bin/env python3
"""Purge orphaned SWA preview environments by invoking the official
StaticSitesClient (action=close) for each closed PR that had a staging
environment.

Improvements over v1:
- Skips fork PRs (SWA only deploys from the same-repo head branch).
- Caps at the 100 most-recent closed PRs (older ones are already cleaned).
- Classifies and summarises outcomes (ok / rejected / timeout / skip).
- Dry-run prints the plan without touching anything.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

REPO = os.environ["GITHUB_REPOSITORY"]
SWA_TOKEN = os.environ.get("SWA_TOKEN", "")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
DRY = os.environ.get("DRY_RUN", "true") == "true"
API = "https://api.github.com/repos/" + REPO
MAX_PRS = 100          # only sweep the most-recent closed PRs
DOCKER_TIMEOUT = 180   # seconds per close attempt
IMAGE = "mcr.microsoft.com/appsvc/staticappsclient:stable"


def _gh(path, method="GET"):
    req = urllib.request.Request(
        API + path,
        method=method,
        headers={
            "Authorization": "Bearer " + GH_TOKEN,
            "Accept": "application/vnd.github+json",
            "User-Agent": "swa-cleanup",
        },
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read()) if r.read() else None


def _fetch_closed_prs():
    """Return up to MAX_PRS closed PR numbers (same-repo only)."""
    nums = []
    page = 1
    while len(nums) < MAX_PRS and page <= 5:
        req = urllib.request.Request(
            f"{API}/pulls?state=closed&sort=updated&direction=desc"
            f"&per_page=100&page={page}",
            headers={
                "Authorization": "Bearer " + GH_TOKEN,
                "Accept": "application/vnd.github+json",
                "User-Agent": "swa-cleanup",
            },
        )
        with urllib.request.urlopen(req) as r:
            prs = json.loads(r.read())
        if not prs:
            break
        for p in prs:
            # skip fork PRs — SWA only creates envs for same-repo pushes
            head_repo = (p.get("head") or {}).get("repo") or {}
            if head_repo.get("full_name") != REPO:
                continue
            nums.append(p["number"])
            if len(nums) >= MAX_PRS:
                break
        if len(prs) < 100:
            break
        page += 1
    return nums


def _close_pr(pr_num, workspace_dir):
    """Run StaticSitesClient close for one PR. Returns (ok|rejected|timeout|error, detail)."""
    evd = os.path.join(workspace_dir, str(pr_num))
    os.makedirs(evd, exist_ok=True)

    # fetch PR + repo payloads for the fake event
    pr = _gh(f"/pulls/{pr_num}")
    repo = _gh("")
    with open(os.path.join(evd, "event.json"), "w") as f:
        json.dump({
            "event_name": "pull_request",
            "action": "closed",
            "number": pr_num,
            "pull_request": pr,
            "repository": repo,
        }, f)

    cmd = [
        "docker", "run", "--rm",
        "-e", "INPUT_ACTION=close",
        "-e", "INPUT_AZURE_STATIC_WEB_APPS_API_TOKEN=" + SWA_TOKEN,
        "-e", "GITHUB_EVENT_PATH=/w/event.json",
        "-e", "GITHUB_EVENT_NAME=pull_request",
        "-e", "GITHUB_ACTIONS=true",
        "-e", "CI=true",
        "-e", "GITHUB_REPOSITORY=" + REPO,
        "-v", f"{evd}:/w",
        "--entrypoint", "/bin/sh",
        IMAGE,
        "-c", "cd /bin/staticsites && ./StaticSitesClient close 2>&1",
    ]
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=DOCKER_TIMEOUT,
            env={**os.environ, "INPUT_AZURE_STATIC_WEB_APPS_API_TOKEN": SWA_TOKEN},
        )
    except subprocess.TimeoutExpired:
        return "timeout", ""

    out = (r.stdout + r.stderr).strip()
    bad = "BadRequest" in out or "rejected" in out or "Error" in out
    status = "rejected" if bad else ("ok" if r.returncode == 0 else "error")
    return status, out


def main():
    if not SWA_TOKEN:
        print("::warning::AZURE_STATIC_WEB_APPS_API_TOKEN missing — nothing to purge.")
        return 0
    if not GH_TOKEN:
        print("::error::GITHUB_TOKEN / GH_TOKEN missing.")
        return 1

    nums = _fetch_closed_prs()
    print(f"Closed same-repo PRs to check: {len(nums)}")
    if DRY:
        for n in nums:
            print(f"  [dry] would close PR #{n}")
        print(f"[dry] {len(nums)} environments would be checked")
        return 0

    ws = os.path.join(
        os.environ.get("GITHUB_WORKSPACE") or tempfile.mkdtemp(prefix="swaclose"),
        ".swa-events",
    )
    os.makedirs(ws, exist_ok=True)

    counters = {"ok": 0, "rejected": 0, "timeout": 0, "error": 0}
    details = []
    for n in nums:
        status, out = _close_pr(n, ws)
        counters[status] = counters.get(status, 0) + 1
        detail = f"PR #{n} -> {status.upper()}"
        if status in ("rejected", "error"):
            last_lines = "\n".join(out.splitlines()[-6:])
            detail += f"\n    {last_lines}"
        details.append(detail)
        print(detail)

    shutil.rmtree(ws, ignore_errors=True)

    print(f"\n--- SWA staging cleanup summary ---")
    print(f"  ok:       {counters['ok']}")
    print(f"  rejected: {counters['rejected']}")
    print(f"  timeout:  {counters['timeout']}")
    print(f"  error:    {counters['error']}")
    print(f"  total:    {sum(counters.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
