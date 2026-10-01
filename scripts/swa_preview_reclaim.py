#!/usr/bin/env python3
"""Free a Static Web Apps preview slot before deploying a PR preview.

Why this is needed
------------------
Azure Static Web Apps on the free plan allows only 3 preview environments
(https://learn.microsoft.com/azure/static-web-apps/quotas). When all 3 are in
use Azure rejects the upload before it transfers anything:

    This Static Web App already has the maximum number of staging environments

AUT-4827 added a reclaim step, but its rule was wrong and freed nothing
(AUT-4799): it ranked every *open PR* and evicted the least-recently-updated
ones. Most open PRs hold no environment at all, so those evictions were no-ops
and the 3 real slots stayed full. Verified against the live Static Web App on
2026-10-01: 8 open PRs, of which exactly 3 held a reachable staging URL
(#123, #139, #141 - the cap), and the PR the old rule evicted as stalest
(#123) was the only open PR holding a releasable slot.

The nightly azure-swa-cleanup sweep cannot cover the gap either: it only
closes recently *closed* PRs, whose environments are already gone, so all 100
of its calls are no-ops that report success.

What this does
--------------
Preview environments are a fixed-size cache keyed by PRs that actually hold an
environment, not by PRs that are merely open:

  1. Read each open same-repo PR's staging URL from its newest "Your stage site
     is ready!" comment and probe it.
  2. A PR with a reachable URL holds a slot. A PR without one does not, and is
     never an eviction candidate.
  3. Keep the current PR plus the (PREVIEW_LIMIT - 1) most recently updated
     slot holders; evict the remaining holders, least recently updated first.
  4. Confirm each eviction released the slot by polling the victim's staging
     URL until it stops serving.

Step 4 is required because Azure releases the slot asynchronously. v1 counted
an eviction as successful from the client's exit code, then uploaded three
seconds later while the environment was still being torn down.

Never blocks the deploy: failures are reported and the upload is still
attempted, since the current PR may already hold a slot. Production is never
touched and closed PRs are never evicted.

Env vars:
  SWA_TOKEN             AZURE_STATIC_WEB_APPS_API_TOKEN (required)
  GH_TOKEN              GITHUB_TOKEN (required)
  GITHUB_REPOSITORY     owner/name (required)
  CURRENT_PR            the PR being deployed (required)
  PREVIEW_LIMIT         preview env cap for the plan (default 3, free plan)
  GITHUB_STEP_SUMMARY   optional; results are mirrored here
"""
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# swa_dataplane_cleanup reads required env vars at module scope, so the import
# is deferred until main() - the unit tests import this module with no tokens.
_close_pr = _gh = None


def _load_deps():
    global _close_pr, _gh
    if _gh is None:
        from swa_dataplane_cleanup import _close_pr as close_fn, _gh as gh_fn
        _close_pr, _gh = close_fn, gh_fn


_STAGING_URL_RE = re.compile(r"https://[a-z0-9.-]+\.azurestaticapps\.net[^\s)\"'>]*")
_PROBE_TIMEOUT = 20
_RELEASE_TIMEOUT = 150   # Azure tears an environment down asynchronously.
_PROBE_INTERVAL = 10

_lines = []


def say(msg=""):
    print(msg)
    _lines.append(msg)


def flush_summary():
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as fh:
            fh.write("\n".join(_lines) + "\n")


def staging_url_from_comments(comments):
    """Newest SWA staging URL in a comment list, or None if there is not one."""
    for comment in reversed(comments or []):
        found = _STAGING_URL_RE.search(comment.get("body") or "")
        if found:
            return found.group(0).rstrip("/.,")
    return None


def serving(url):
    """True if the staging endpoint still answers with a success status."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "swa-reclaim"})
        with urllib.request.urlopen(req, timeout=_PROBE_TIMEOUT) as resp:
            return 200 <= resp.status < 400
    except urllib.error.HTTPError as exc:
        return 200 <= exc.code < 400
    except Exception:  # DNS, TLS, connection reset -> treat as not serving.
        return False


def await_release(url):
    """Poll until the victim's staging URL stops serving. True if released."""
    deadline = time.time() + _RELEASE_TIMEOUT
    while True:
        if not serving(url):
            return True
        if time.time() >= deadline:
            return False
        time.sleep(_PROBE_INTERVAL)


def select_victims(holders, current_pr, preview_limit):
    """Split live slot holders into (kept, evicted), evicting LRU-first.

    holders must be ordered most-recently-updated first. The current PR always
    keeps its slot, even when it is the stalest holder.
    """
    others = [n for n in holders if n != current_pr]
    keep = others[: max(0, preview_limit - 1)]
    return keep, others[len(keep):]


def main():
    _load_deps()
    current_pr = int(os.environ["CURRENT_PR"])
    preview_limit = int(os.environ.get("PREVIEW_LIMIT", "3"))
    repo = os.environ["GITHUB_REPOSITORY"]

    say("### SWA preview-slot reclaim")
    say("")
    say(f"Preview limit **{preview_limit}** (free plan). Deploying PR **#{current_pr}**.")
    say("")

    open_prs = _gh("/pulls?state=open&per_page=100&sort=updated&direction=desc") or []
    same_repo = [
        pr for pr in open_prs
        if ((pr.get("head") or {}).get("repo") or {}).get("full_name") == repo
    ]
    say(f"Open same-repo PRs: **{len(same_repo)}** "
        f"(the cap counts environments, not PRs)")

    urls = {}
    holders = []
    for pr in same_repo:
        url = staging_url_from_comments(
            _gh(f"/issues/{pr['number']}/comments?per_page=100")
        )
        if url and serving(url):
            urls[pr["number"]] = url
            holders.append(pr["number"])
            say(f"- PR #{pr['number']} **holds a slot** - {url}")
        else:
            say(f"- PR #{pr['number']} holds no live environment - not a candidate")

    keep, victims = select_victims(holders, current_pr, preview_limit)
    say("")
    say(f"Slots in use: **{len(holders)}** / {preview_limit}.")
    if not victims:
        say("Nothing to reclaim.")
        flush_summary()
        return 0

    say("")
    say(f"Keeping {sorted(keep) or 'none'}; evicting **{len(victims)}** "
        f"least-recently-updated slot(s): {victims}")
    say("")

    workspace = os.path.join(
        os.environ.get("GITHUB_WORKSPACE") or tempfile.mkdtemp(prefix="swa-reclaim"),
        ".swa-reclaim-events",
    )
    os.makedirs(workspace, exist_ok=True)

    freed, unreleased = [], []
    try:
        for number in victims:
            status, detail = _close_pr(number, workspace)
            if status != "ok":
                say(f"- PR #{number} -> close **{status.upper()}**, slot NOT released")
                unreleased.append(number)
                tail = "\n".join((detail or "").splitlines()[-6:])
                if tail:
                    say("  ```")
                    for line in tail.splitlines():
                        say("  " + line)
                    say("  ```")
                continue
            # Client exit 0 does not mean Azure has released the slot.
            released = await_release(urls.get(number, ""))
            say(f"- PR #{number} -> close OK, staging URL "
                f"{'stopped serving (slot released)' if released else 'STILL SERVING'}")
            (freed if released else unreleased).append(number)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    say("")
    say(f"Freed **{len(freed)}** slot(s); **{len(unreleased)}** not released.")
    if unreleased:
        say("")
        say("> An evicted PR regains its preview on its next push. Production "
            "and closed PRs are never touched.")
    flush_summary()

    if unreleased:
        print("::warning::SWA preview reclaim incomplete for PR(s) "
              + ", ".join("#" + str(n) for n in unreleased))
    return 0


if __name__ == "__main__":
    sys.exit(main())