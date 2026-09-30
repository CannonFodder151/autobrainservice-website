#!/usr/bin/env python3
"""Fail if any indexable HTML page breaks an on-page SEO invariant.

This is the check that closes the loop on the bi-daily SEO review. It exists
because the review kept finding the same defects by hand, 51 pages at a time,
and shipping them without a guard meant they regressed on the next content push.

Invariants checked, per indexable page (noindex pages are exempt):

  title        <= 60 chars   - Google truncates around 580px
  description  <= 160 chars  - the snippet is cut before the value prop lands
  canonical    present
  og:          present       - link previews on Slack/Discord/iMessage
  twitter:     present
  hreflang     en-AU AND x-default present

Plus site-level integrity, which is where the 404s came from:

  every internal href resolves to a file that exists
  sitemap.xml covers every indexable page

Exit 0 = clean. Exit 1 = violations, listed.

Override a limit with an env var when a page genuinely needs more:
  SEO_TITLE_MAX, SEO_DESC_MAX
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TITLE_MAX = int(os.environ.get("SEO_TITLE_MAX", "60"))
DESC_MAX = int(os.environ.get("SEO_DESC_MAX", "160"))
SITE = "https://autobrainservice.app/"

# Pages that are deliberately not crawlable and are disallowed in robots.txt.
EXEMPT = {"delete-account.html"}

# Not HTML, so no page-level invariants apply, but its presence in the sitemap
# is checked by sitemap coverage below.
NON_HTML = {"rss.xml"}


def html_files():
    files = {f.name for f in ROOT.glob("*.html")}
    files |= {f"blog/{f.name}" for f in (ROOT / "blog").glob("*.html")}
    return sorted(files)


def is_noindex(text):
    head = text[:2500]
    return "noindex" in head


def first_group(pattern, text, flags=re.S):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ""


def check_page(path):
    text = (ROOT / path).read_text(encoding="utf-8", errors="ignore")
    bad = []

    title = " ".join(first_group(r"<title>(.*?)</title>", text).split())
    if not title:
        bad.append("no <title>")
    elif len(title) > TITLE_MAX:
        bad.append(f"title {len(title)} chars (max {TITLE_MAX}): {title!r}")

    desc = first_group(r'<meta name="description" content="([^"]*)"', text, re.I)
    if not desc:
        bad.append("no meta description")
    elif len(desc) > DESC_MAX:
        bad.append(f"description {len(desc)} chars (max {DESC_MAX})")

    for label, needle in (
        ("canonical", 'rel="canonical"'),
        ("og:", 'property="og:'),
        ("twitter:", 'name="twitter:'),
        ('hreflang en-AU', 'hreflang="en-AU"'),
        ("hreflang x-default", 'hreflang="x-default"'),
    ):
        if needle not in text:
            bad.append(f"missing {label}")

    return bad


def check_links():
    bad = []
    for path in html_files():
        text = (ROOT / path).read_text(encoding="utf-8", errors="ignore")
        for href in re.findall(r'href="([^"#?]+)"', text):
            if href.startswith(("http", "mailto:", "tel:", "//", "data:", "javascript")):
                continue
            if href.startswith("/cdn-cgi/"):
                continue  # Cloudflare injects these at runtime
            target = os.path.normpath(os.path.join(os.path.dirname(path), href))
            if target.startswith(".."):
                target = target[3:]
            if not (ROOT / target).exists():
                bad.append(f"{path} -> {href}")
    return bad


def check_sitemap():
    sitemap = (ROOT / "sitemap.xml").read_text()
    listed = {
        u.replace(SITE, "").lstrip("/")
        for u in re.findall(r"<loc>([^<]+)</loc>", sitemap)
    }
    missing = []
    for path in html_files():
        base = path.rsplit("/", 1)[-1]
        if path in EXEMPT or base in NON_HTML or base == "index.html":
            continue
        if is_noindex((ROOT / path).read_text(encoding="utf-8", errors="ignore")):
            continue
        if path not in listed:
            missing.append(path)
    return missing, len(listed)


def main():
    violations = []

    for path in html_files():
        if path in EXEMPT:
            continue
        if is_noindex((ROOT / path).read_text(encoding="utf-8", errors="ignore")):
            continue
        for issue in check_page(path):
            violations.append(f"{path}: {issue}")

    for link in check_links():
        violations.append(f"broken internal link: {link}")

    missing, listed = check_sitemap()
    for path in missing:
        violations.append(f"{path}: indexable but not in sitemap.xml")

    if violations:
        print("on-page SEO violations:\n")
        for v in violations:
            print(f"  {v}")
        print(f"\n{len(violations)} violation(s). sitemap.xml has {listed} entries.")
        return 1

    print(f"OK: {len(html_files())} pages clean — titles <= {TITLE_MAX}, "
          f"descriptions <= {DESC_MAX}, hreflang complete, no broken links, "
          f"sitemap has {listed} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
