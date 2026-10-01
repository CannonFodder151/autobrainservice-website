#!/usr/bin/env python3
"""Free a Static Web Apps preview slot before deploying a PR preview (AUT-4827).

Why this is needed
------------------
Azure Static Web Apps on the **free plan allows only 3 preview environments**
(https://learn.microsoft.com/azure/static-web-apps/quotas). This repo routinely
has more than 3 open PRs, so Azure rejects the upload with:

    This Static Web App already has the maximum number of staging environments

The nightly azure-swa-cleanup sweep cannot fix this: it calls `close` on the
100 most-recently-updated *closed* PRs, whose environments were deleted long ago
(those calls are no-ops that report success), and it never touches open PRs. So
the cap stayed permanently saturated.

What this does
--------------
Treats preview environments as a fixed-size cache:

  * rank open PRs by most-recently-updated,
  * keep the current PR plus the (LIMIT - 1) most recent others,
  * close the staging environment of every *other* open PR.

Eviction is least-recently-updated first, so the PRs people are actively
reviewing keep their preview URL. An evicted PR regains a preview on its next
push. Only *other open* PRs are ever touched — production and closed PRs are
never modified.

Env vars:
  SWA_TOKEN        AZURE_STATIC_WEB_APPS_API_TOKEN (required)
  GH_TOKEN         GITHUB_TOKEN (required)
  GITHUB_REPOSITORY owner/name (required)
  CURRENT_PR       the PR being deployed (required)
  PREVIEW_LIMIT    preview env cap for the plan (default 3, free plan)
  GITHUB_STEP_SUMMARY  optional; results are mirrored here
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swa_dataplane_cleanup import _close_pr, _gh  # noqa: E402

CURRENT_PR = int(os.environ["CURRENT_PR"])
PREVIEW_LIMIT = int(os.environ.get("PREVIEW_LIMIT", "3"))
REPO = os.environ["GITHUB_REPOSITORY"]

_lines = []


def say(msg=""):
    print(msg)
    _lines.append(msg)


def flush_summary():
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as fh:
            fh.write("\n".join(_lines) + "\n")


def main():
    say("### SWA preview-slot reclaim")
    say("")
    say(f"Preview limit **{PREVIEW_LIMIT}** (free plan). Deploying PR **#{CURRENT_PR}**.")
    say("")

    prs = _gh("/pulls?state=open&per_page=100&sort=updated&direction=desc") or []
    same_repo = [
        p for p in prs
        if ((p.get("head") or {}).get("repo") or {}).get("full_name") == REPO
    ]
    if len(same_repo) <= PREVIEW_LIMIT:
        say(f"{len(same_repo)} open same-repo PR(s) <= limit — nothing to reclaim.")
        flush_summary()
        return 0

    # Most recently updated first; the current PR always keeps its slot.
    ordered = [p["number"] for p in same_repo]
    if CURRENT_PR in ordered:
        ordered.remove(CURRENT_PR)
        ordered.insert(0, CURRENT_PR)

    keep = set(ordered[:PREVIEW_LIMIT])
    victims = [n for n in ordered if n not in keep]

    say("Open same-repo PRs (most recently updated first):")
    for n in ordered:
        mark = "keep  " if n in keep else "evict "
        say(f"- `{mark}` PR #{n}")
    say("")
    say(f"Evicting **{len(victims)}** staging environment(s) to free slot(s).")
    say("")
    say("> Evicted PRs lose their preview URL until their next push. Production "
        "and closed PRs are never touched.")
    say("")

    ws = os.path.join(
        os.environ.get("GITHUB_WORKSPACE") or tempfile.mkdtemp(prefix="swa-reclaim"),
        ".swa-reclaim-events",
    )
    os.makedirs(ws, exist_ok=True)

    failed = []
    try:
        for n in victims:
            status, out = _close_pr(n, ws)
            ok = status == "ok"
            say(f"- PR #{n} -> **{status.upper()}**")
            if not ok:
                failed.append(n)
                tail = "\n".join((out or "").splitlines()[-6:])
                if tail:
                    say("  ```")
                    for line in tail.splitlines():
                        say("  " + line)
                    say("  ```")
    finally:
        shutil.rmtree(ws, ignore_errors=True)

    say("")
    say(f"Freed **{len(victims) - len(failed)}** slot(s), failed **{len(failed)}**.")
    flush_summary()

    # Never block the deploy: if reclaim failed we still want the upload
    # attempted (the PR may already hold a slot). Report and move on.
    if failed:
        print("::warning::SWA preview reclaim incomplete for PR(s) "
              + ", ".join("#" + str(n) for n in failed))
    return 0


if __name__ == "__main__":
    sys.exit(main())