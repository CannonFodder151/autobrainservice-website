#!/usr/bin/env python3
"""Branch hygiene: warn -> close stale PRs (>14d idle branches), delete orphan branches."""
import json
import os
import sys
import time
import urllib.request

REPO = os.environ["GITHUB_REPOSITORY"]
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
DRY = os.environ.get("DRY_RUN", "true") == "true"
STALE_DAYS = 14
API = "https://api.github.com/repos/" + REPO
MARKER = "<!-- branch-hygiene -->"


def call(method, path, body=None, ok=(200,)):
    req = urllib.request.Request(
        API + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            "Authorization": "Bearer " + TOKEN,
            "Accept": "application/vnd.github+json",
            "User-Agent": "branch-hygiene",
        },
    )
    try:
        with urllib.request.urlopen(req) as r:
            data = r.read()
            return r.status, json.loads(data) if data else None
    except urllib.error.HTTPError as e:
        return e.code, None


def main():
    _, repo = call("GET", "")
    default = repo["default_branch"]
    _, prs = call("GET", "/pulls?state=open&per_page=100")
    by_branch = {
        p["head"]["ref"]: p
        for p in prs or []
        if p["head"]["repo"] and p["head"]["repo"]["full_name"] == REPO
    }
    _, branches = call("GET", "/branches?per_page=100")
    cutoff = time.time() - STALE_DAYS * 86400
    actions = []
    for b in branches:
        name = b["name"]
        if name == default or b.get("protected"):
            continue
        _, c = call("GET", "/commits/" + name)
        ts = time.mktime(time.strptime(c["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ"))
        if ts >= cutoff:
            continue
        pr = by_branch.get(name)
        delete_ok = (404, 403, 422)
        if pr:
            n = pr["number"]
            _, comments = call("GET", f"/issues/{n}/comments?per_page=100")
            warned = any(MARKER in (x.get("body") or "") for x in comments or [])
            if not warned:
                actions.append(f"warn PR #{n} ({name})")
                if not DRY:
                    call(
                        "POST",
                        f"/issues/{n}/comments",
                        {"body": f"Warning: branch `{name}` has had no activity for {STALE_DAYS} days. This PR will be automatically closed and its branch deleted by scheduled branch hygiene unless it sees activity. {MARKER}"},
                    )
            else:
                actions.append(f"close PR #{n} + delete branch {name}")
                if not DRY:
                    call("POST", f"/issues/{n}/comments", {"body": f"Auto-closed by scheduled branch hygiene: branch `{name}` inactive past the {STALE_DAYS}-day warning. Reopen or push to restore. Closing removes the SWA staging environment."})
                    call("PATCH", f"/pulls/{n}", {"state": "closed"})
                    call("DELETE", "/git/refs/heads/" + name, ok=delete_ok + (200, 204))
        else:
            actions.append(f"delete branch {name} (no open PR)")
            if not DRY:
                call("DELETE", "/git/refs/heads/" + name, ok=delete_ok + (200, 204))
    print("[DRY RUN] planned:\n" + "\n".join(actions) if DRY and actions else ("\n".join(actions) if actions else "no stale branches"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
