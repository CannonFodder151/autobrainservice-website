#!/usr/bin/env python3
"""Regenerate the release blocks in changelog.html from CHANGELOG.md.

CHANGELOG.md follows Keep a Changelog (see the autobrain repo). Only tagged
releases are rendered; [Unreleased] is intentionally excluded from the public
site. Idempotent: run from the repo root (or anywhere) and changelog.html is
rewritten between the CHANGELOG-START / CHANGELOG-END markers.

Only the MAX_RELEASES most recent releases are rendered. The mirror
CHANGELOG.md is a full, append-only file synced from CannonFodder151/autobrain;
rendering all of it produced a ~143 KB single page that ate the crawl budget for
every other page on the site. Older releases stay readable on GitHub.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "CHANGELOG.md"
HTML = ROOT / "changelog.html"

START = "<!-- CHANGELOG-START -->"
END = "<!-- CHANGELOG-END -->"

# ponytail: 60 releases (~6 months at the current ~10-releases/week rate).
# Changelog is not a compliance log — full history lives in the autobrain repo.
# Raise it if the public page ever needs a deeper window.
MAX_RELEASES = int(os.environ.get("CHANGELOG_MAX_RELEASES", "60"))
FULL_HISTORY_URL = "https://github.com/CannonFodder151/autobrain/blob/main/CHANGELOG.md"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s):
    return re.sub(r"`([^`]+)`", lambda m: "<code>" + esc(m.group(1)) + "</code>", esc(s))


def parse_items(text):
    items = []
    cur = None
    for line in text.splitlines():
        if line.strip().startswith("- "):
            if cur is not None:
                items.append(cur)
            cur = line.strip()[2:]
        elif cur is not None and line.strip():
            cur += " " + line.strip()
    if cur is not None:
        items.append(cur)
    return items


def build_release(sec):
    title, _, rest = sec.partition("\n")
    m = re.match(r"\[(\d+\.\d+\.\d+)\]", title)
    if not m:
        return None
    ver = m.group(1)
    dm = re.search(r"(\d{4}-\d{2}-\d{2})", title)
    date = dm.group(1) if dm else ""
    subs = ""
    for part in re.split(r"(?m)^### ", rest)[1:]:
        heading, _, items = part.partition("\n")
        lis = "".join(f"<li>{inline(i)}</li>" for i in parse_items(items))
        subs += f"      <h3>{esc(heading.strip())}</h3>\n      <ul>\n        {lis}\n      </ul>\n"
    return (
        f'    <div class="release">\n'
        f"      <h2>v{ver}</h2>\n"
        f'      <div class="date">{date}</div>\n'
        f"{subs}    </div>"
    )


def main():
    md = MD.read_text()
    all_blocks = [b for b in (build_release(s) for s in re.split(r"(?m)^## ", md)[1:]) if b]
    blocks = all_blocks[:MAX_RELEASES]
    hidden = len(all_blocks) - len(blocks)
    html = HTML.read_text()
    if START not in html or END not in html:
        sys.exit(f"{HTML.name}: missing {START} / {END} markers")
    head, _, rest = html.partition(START)
    _, _, tail = rest.partition(END)
    body = "\n\n".join(blocks)
    if hidden > 0:
        body += (
            f'\n\n    <div class="release">\n'
            f"      <h2>Older releases</h2>\n"
            f'      <div class="date">{len(all_blocks)} total</div>\n'
            f"      <p>This page shows the {len(blocks)} most recent releases. "
            f'The {hidden} older ones are in the <a href="{FULL_HISTORY_URL}" '
            f'rel="noopener">full changelog</a>.</p>\n'
            f"    </div>"
        )
    HTML.write_text(f"{head}{START}\n{body}\n    {END}{tail}")
    print(
        f"wrote {len(blocks)} of {len(all_blocks)} releases to {HTML.name}"
        + (f" ({hidden} older releases linked to the repo)" if hidden else "")
    )


if __name__ == "__main__":
    main()
