#!/usr/bin/env python3
"""Regenerate the release blocks in changelog.html from CHANGELOG.md.

CHANGELOG.md follows Keep a Changelog (see the autobrain repo). Only tagged
releases are rendered; [Unreleased] is intentionally excluded from the public
site. Idempotent: run from the repo root (or anywhere) and changelog.html is
rewritten between the CHANGELOG-START / CHANGELOG-END markers.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "CHANGELOG.md"
HTML = ROOT / "changelog.html"

START = "<!-- CHANGELOG-START -->"
END = "<!-- CHANGELOG-END -->"


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
    blocks = [b for b in (build_release(s) for s in re.split(r"(?m)^## ", md)[1:]) if b]
    html = HTML.read_text()
    if START not in html or END not in html:
        sys.exit(f"{HTML.name}: missing {START} / {END} markers")
    head, _, rest = html.partition(START)
    _, _, tail = rest.partition(END)
    body = "\n\n".join(blocks)
    HTML.write_text(f"{head}{START}\n{body}\n    {END}{tail}")
    print(f"wrote {len(blocks)} releases to {HTML.name}")


if __name__ == "__main__":
    main()
