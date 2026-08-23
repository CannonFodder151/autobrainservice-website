#!/usr/bin/env python3
"""SWA data-plane cleanup: probe list endpoints, purge orphaned preview envs of closed PRs."""
import json
import os
import sys
import urllib.request

REPO = os.environ["GITHUB_REPOSITORY"]
SWA_TOKEN = os.environ.get("SWA_TOKEN", "")
GH_TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
DRY = os.environ.get("DRY_RUN", "true") == "true"
API = "https://api.github.com/repos/" + REPO
FALLBACK_HOST = "happy-glacier-0f26af910.azurestaticapps.net"


def http(url, method="GET", token=None, body=None):
    req = urllib.request.Request(
        url,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={
            **({"Authorization": "Bearer " + token} if token else {}),
            "User-Agent": "swa-cleanup",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 0, str(e).encode()


def main():
    if not SWA_TOKEN:
        print("::warning::AZURE_STATIC_WEB_APPS_API_TOKEN missing - cannot reach data plane.")
        return 0
    dp = "https://" + FALLBACK_HOST
    print(f"data plane: {dp} dry={DRY}")

    print("## data-plane list probes")
    for ep in ["staging-environments", "list_environments", "environments", "list_builds", "builds"]:
        code, body = http(f"{dp}/{ep}?api-version=1.0", token=SWA_TOKEN)
        line = f"probe GET /{ep} -> {code}"
        if code == 200:
            line += " | " + body.decode(errors="replace")[:1500]
            print(line)

    if DRY:
        print("## close-variant diagnostics (route from StaticSitesClient.dll)")
        for pr in [33, 999999]:
            for label, path, payload in [
                ("json-camel-bearer", "/api/pullrequest/close?apiVersion=v1&deploymentCorrelationId=11111111-1111-1111-1111-111111111111", {"pullRequestId": pr}),
                ("query-param-bearer", f"/api/pullrequest/close?apiVersion=v1&pullRequestId={pr}", None),
                ("json-pascal-bearer", "/api/pullrequest/close?apiVersion=v1", {"PullRequestId": pr}),
            ]:
                req = urllib.request.Request(dp + path, method="POST",
                    data=json.dumps(payload).encode() if payload else b"",
                    headers={"Authorization": "Bearer " + SWA_TOKEN, "Content-Type": "application/json", "User-Agent": "swa-cleanup"})
                try:
                    with urllib.request.urlopen(req, timeout=30) as r:
                        print(f"PR#{pr} {label} -> {r.status} {r.read()[:200]!r}")
                        break
                except urllib.error.HTTPError as e:
                    print(f"PR#{pr} {label} -> {e.code} {e.read()[:200]!r}")
                except Exception as e:
                    print(f"PR#{pr} {label} -> ERR {e}")

    page = 1
    total = purged = 0
    while page <= 5:
        req = urllib.request.Request(
            f"{API}/pulls?state=closed&per_page=100&page={page}",
            headers={"Authorization": "Bearer " + GH_TOKEN, "User-Agent": "swa-cleanup"},
        )
        with urllib.request.urlopen(req) as r:
            prs = json.load(r)
        if not prs:
            break
        for p in prs:
            n = p["number"]
            total += 1
            if DRY:
                print(f"[dry] would close_pull_request PR #{n}")
                continue
            code, _ = http(f"{dp}/close_pull_request?api-version=1.0&pullrequestId={n}", method="POST", token=SWA_TOKEN)
            if code in (200, 204):
                purged += 1
            elif code not in (404,):
                print(f"close_pull_request PR #{n} -> unexpected {code}")
        if len(prs) < 100:
            break
        page += 1
    print(f"[dry] would re-close {total} closed PR(s)" if DRY else f"re-closed {total} closed PR(s) ({purged} ok) against the data plane")
    print("open PRs untouched - branch-hygiene closes those properly so close_pull_request_job cascades.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
