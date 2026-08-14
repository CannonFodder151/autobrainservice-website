#!/usr/bin/env python3
"""Flip the Garage Issues feature badge between "Coming soon" and "Now live".

Auto "out now" update: once a RELEASED changelog entry (a tagged
"## [x.y.z]" section — never [Unreleased]) mentions the feature, every page
badge carrying `data-garage-issues="soon"` is rewritten to "live" at deploy
time. The site's CHANGELOG.md is auto-synced from the autobrain repo, so the
flip happens automatically on the next deploy after the feature ships.

Idempotent. Run from the repo root (or anywhere):
  python3 scripts/gen_feature_status.py [--selftest]
"""
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "CHANGELOG.md"
PAGES = [ROOT / "index.html", ROOT / "community-garage.html"]
# ponytail: match-release-note-phrase. When the feature ships, the autobrain
# changelog entry should carry one of these phrases; extend if wording differs.
MARKERS = ("garage issues", "issues feed", "issues blog")

BADGE = re.compile(
    r'<div class="(soon|live)"([^>]*data-garage-issues=")(soon|live)("[^>]*)>(Coming soon|Now live)</div>'
)


def released_mentions_marker(text):
    for part in re.split(r"(?m)^## ", text)[1:]:
        header, _, body = part.partition("\n")
        if "Unreleased" in header:
            continue
        low = body.lower()
        if any(m in low for m in MARKERS):
            return True
    return False


def flip(path, out):
    s = path.read_text()

    def repl(m):
        pre, state, post = m.group(2), m.group(3), m.group(4)
        if out == "live":
            return f'<div class="live"{pre}live{post}>Now live</div>'
        return f'<div class="soon"{pre}soon{post}>Coming soon</div>'

    n, count = BADGE.subn(repl, s)
    if count:
        path.write_text(n)
    return count > 0


def selftest():
    soon = (
        "# Changelog\n\n## [Unreleased]\n- Garage Issues feed in the works\n\n"
        "## [0.3.59] - 2026-08-14\n- Rego lookup fix\n"
    )
    live = (
        "# Changelog\n\n## [Unreleased]\n- more work\n\n"
        "## [0.4.0] - 2026-09-01\n- Community Garage: Garage Issues feed (AUT-627)\n"
    )
    assert not released_mentions_marker(soon), "unreleased-only mention must not flip"
    assert released_mentions_marker(live), "released mention must flip"
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.html"
        p.write_text('<div class="soon" style="margin:0" data-garage-issues="soon">Coming soon</div>')
        assert flip(p, "live") and 'class="live"' in p.read_text() and 'data-garage-issues="live"' in p.read_text() and "Now live" in p.read_text()
        assert flip(p, "soon") and 'class="soon"' in p.read_text() and 'data-garage-issues="soon"' in p.read_text() and "Coming soon" in p.read_text()
        p.write_text('<div class="soon" style="margin:0">Coming soon</div>')
        assert not flip(p, "live"), "badge without the data marker must be untouched"
    print("gen_feature_status: selftest OK")


def main():
    if "--selftest" in sys.argv:
        selftest()
        return 0
    out = "live" if (MD.exists() and released_mentions_marker(MD.read_text())) else "soon"
    for p in PAGES:
        if p.exists() and flip(p, out):
            print(f"gen_feature_status: {p.name} -> Garage Issues {out.upper()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
