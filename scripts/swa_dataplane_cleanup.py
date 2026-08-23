#!/usr/bin/env python3
"""Purge orphaned SWA preview environments by invoking the official StaticSitesClient (action=close) per closed PR."""
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


def main():
    if not SWA_TOKEN:
        print("::warning::AZURE_STATIC_WEB_APPS_API_TOKEN missing - cannot purge.")
        return 0
    page = 1
    nums = []
    while page <= 5:
        req = urllib.request.Request(
            f"{API}/pulls?state=closed&per_page=100&page={page}",
            headers={"Authorization": "Bearer " + GH_TOKEN, "User-Agent": "swa-cleanup"},
        )
        with urllib.request.urlopen(req) as r:
            prs = json.load(r)
        if not prs:
            break
        nums += [p["number"] for p in prs]
        if len(prs) < 100:
            break
        page += 1
    print(f"closed PRs to re-close: {len(nums)}")

    ws = tempfile.mkdtemp(prefix="swaclose")
    ok = fail = 0
    for n in nums:
        if DRY:
            print(f"[dry] would run official close for PR #{n}")
            continue
        ev = os.path.join(ws, f"event-{n}.json")
        with open(ev, "w") as f:
            json.dump({"event_name": "pull_request", "action": "closed", "pull_request": {"number": n}}, f)
        cmd = [
            "docker", "run", "--rm",
            "-e", "INPUT_ACTION=close",
            "-e", "INPUT_AZURE_STATIC_WEB_APPS_API_TOKEN",
            "-e", "GITHUB_EVENT_PATH=/w/event.json",
            "-e", "GITHUB_EVENT_NAME=pull_request",
            "-e", "GITHUB_WORKSPACE=/w",
            "-v", f"{ev}:/w/event.json",
            "mcr.microsoft.com/appsvc/staticappsclient:stable",
        ]
        r = subprocess.run(cmd, env={**os.environ, "INPUT_AZURE_STATIC_WEB_APPS_API_TOKEN": SWA_TOKEN},
                           capture_output=True, text=True, timeout=180)
        out = [l for l in (r.stdout + r.stderr).strip().splitlines() if l.strip()]
        print(f"PR #{n} -> rc={r.returncode}")
        for line in out[-8:]:
            print(f"    {line[:200]}")
        if r.returncode == 0:
            ok += 1
        else:
            fail += 1
    shutil.rmtree(ws, ignore_errors=True)
    print("[dry] no purges executed" if DRY else f"purge done: {ok} ok, {fail} failed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
