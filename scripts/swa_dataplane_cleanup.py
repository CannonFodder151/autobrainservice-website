#!/usr/bin/env python3
"""Purge orphaned SWA preview environments by invoking the official
StaticSitesClient (action=close) for each closed PR that had a staging
environment.

Improvements over v1:
- Skips fork PRs (SWA only deploys from the same-repo head branch).
- Caps at the 100 most-recent closed PRs (older ones are already cleaned).
- Classifies and summarises outcomes (ok / rejected / timeout / skip).
- Dry-run prints the plan without touching anything.
- One transient GitHub API error no longer aborts the sweep: _gh() retries
  429/502/503/504 and connection errors with backoff + jitter, and main()
  records a per-PR failure and continues.
"""
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

REPO = os.environ["GITHUB_REPOSITORY"]
SWA_TOKEN = os.environ.get("SWA_TOKEN", "")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
DRY = os.environ.get("DRY_RUN", "true") == "true"
API = "https://api.github.com/repos/" + REPO
MAX_PRS = 100          # only sweep the most-recent closed PRs
DOCKER_TIMEOUT = 180   # seconds per close attempt
IMAGE = "mcr.microsoft.com/appsvc/staticappsclient:stable"
RETRY_CODES = {429, 502, 503, 504}   # transient — secondary rate limit / backend blip
AUTH_CODES = {401, 403}              # real config regression — retrying will not help
GH_ATTEMPTS = 4                     # 1 try + 3 retries
GH_BACKOFF = 2.0                    # seconds, doubled each retry


class GhAuthError(RuntimeError):
    """401/403 from GitHub — the token/permission is wrong, not transient."""


def _gh(path, method="GET"):
    """GET a GitHub API path, retrying transient failures with backoff + jitter."""
    req = urllib.request.Request(
        API + path,
        method=method,
        headers={
            "Authorization": "Bearer " + GH_TOKEN,
            "Accept": "application/vnd.github+json",
            "User-Agent": "swa-cleanup",
        },
    )
    last = None
    for attempt in range(GH_ATTEMPTS):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
                return json.loads(body) if body else None
        except urllib.error.HTTPError as e:
            if e.code in AUTH_CODES:
                raise GhAuthError(f"GitHub API {e.code} on {path}") from e
            if e.code not in RETRY_CODES:
                raise
            last = e
            # Retry-After is untrusted and may be an HTTP-date, negative, nan or
            # inf (RFC 9110 allows delta-seconds OR a date). Anything outside
            # (0, 60) falls back to exponential backoff.
            try:
                delay = float(e.headers.get("Retry-After") or 0)
            except (TypeError, ValueError):
                delay = 0.0
            if not 0.0 < delay < 60.0:  # also rejects nan (False), 0, inf, -5
                delay = GH_BACKOFF * 2 ** attempt
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = e
            delay = GH_BACKOFF * 2 ** attempt
        if attempt + 1 == GH_ATTEMPTS:
            break  # doomed call — do not sleep before raising
        delay = min(delay, 60.0) + random.uniform(0, 1)
        print(f"::warning::GitHub API transient failure on {path} "
              f"({last}); retry {attempt + 2}/{GH_ATTEMPTS} in {delay:.1f}s", flush=True)
        time.sleep(delay)
    raise last


def _fetch_closed_prs():
    """Return up to MAX_PRS closed PR numbers (same-repo only)."""
    nums = []
    page = 1
    while len(nums) < MAX_PRS and page <= 5:
        prs = _gh(f"/pulls?state=closed&sort=updated&direction=desc&per_page=100&page={page}")
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

    try:
        nums = _fetch_closed_prs()
    except GhAuthError as e:
        print(f"::error::{e} — check the workflow token permissions.")
        return 1
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

    counters = {"ok": 0, "rejected": 0, "timeout": 0, "error": 0, "skipped": 0}
    details = []
    for n in nums:
        try:
            status, out = _close_pr(n, ws)
        except GhAuthError as e:
            # auth broke mid-sweep: nothing after this can work either
            print(f"::error::{e} — aborting sweep at PR #{n}.")
            print(f"::error::Sweep incomplete: {counters['ok']} environment(s) cleaned before abort.")
            shutil.rmtree(ws, ignore_errors=True)
            return 1
        except urllib.error.HTTPError as e:
            # 404 = the PR/route is gone; nothing to purge, not a failure
            status, out = ("skipped", "") if e.code == 404 else ("error", f"HTTP {e.code}")
        except Exception as e:  # noqa: BLE001 - one bad PR must not kill the sweep
            status, out = "error", f"{type(e).__name__}: {e}"
        counters[status] = counters.get(status, 0) + 1
        detail = f"PR #{n} -> {status.upper()}"
        if status in ("rejected", "error"):
            last_lines = "\n".join(str(out).splitlines()[-6:])
            detail += f"\n    {last_lines}"
        details.append(detail)
        print(detail)

    shutil.rmtree(ws, ignore_errors=True)

    print(f"\n--- SWA staging cleanup summary ---")
    for k in ("ok", "rejected", "timeout", "error", "skipped"):
        print(f"  {k + ':':10s}{counters[k]}")
    print(f"  {'total:':10s}{sum(counters.values())}")

    if counters["error"]:
        print(f"::warning::{counters['error']} PR(s) failed this sweep; "
              f"the next daily run retries them.")
    # only fail the run when nothing at all got cleaned — a partial sweep is
    # still worth more than a red run that skips the remaining 89 PRs
    if nums and counters["ok"] == 0 and counters["error"] == len(nums):
        print("::error::Every PR failed — treating as a hard failure.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
