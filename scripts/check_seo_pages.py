#!/usr/bin/env python3
"""Fail if any indexable HTML page breaks an on-page SEO invariant.

This is the check that closes the loop on the bi-daily SEO review. It exists
because the review kept finding the same defects by hand, 51 pages at a time,
and shipping them without a guard meant they regressed on the next content push.

Invariants checked, per indexable page (noindex pages are exempt):

  title        <= 60 chars   - Google truncates around 580px
  title        no HTML entities - "&amp;" survives naive extraction,
                                 so scrapers show "&amp;" instead of "&"
  description  70..160 chars - too long is cut before the value prop lands,
                                 too short makes Google write the snippet itself
  canonical    present
  og:          present       - link previews on Slack/Discord/iMessage
  twitter:     present
  hreflang     en-AU AND x-default present

Plus site-level integrity, which is where the 404s came from:

  every internal href resolves to a file that exists
  sitemap.xml covers every indexable page
  sitemap.xml lists only indexable pages   - a noindex URL or a feed (rss.xml)
                                              in the sitemap sends mixed signals
                                              and wastes crawl budget

And one security invariant, added after AUT-5045 (a shared demo password was
published in cleartext on an indexable page):

  no email address is followed by a password-shaped literal

The description floor and the sitemap-hygiene rules were added after AUT-5325.
The audit behind it ran against a stale checkout: the three thin descriptions
it reported have since been rewritten by earlier passes, and no floor existed
to hold them there. The title-entity and sitemap defects were live on main.

Exit 0 = clean. Exit 1 = violations, listed.

Override a limit with an env var when a page genuinely needs more:
  SEO_TITLE_MAX, SEO_DESC_MAX, SEO_DESC_MIN
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TITLE_MAX = int(os.environ.get("SEO_TITLE_MAX", "60"))
DESC_MAX = int(os.environ.get("SEO_DESC_MAX", "160"))
DESC_MIN = int(os.environ.get("SEO_DESC_MIN", "70"))
SITE = "https://autobrainservice.app/"

# Pages that are deliberately not crawlable and are disallowed in robots.txt.
EXEMPT = {"delete-account.html"}

# Not HTML, so no page-level invariants apply. Feeds and assets do not belong
# in a sitemap: it is a list of indexable pages, not a list of URLs.
NON_HTML = {"rss.xml"}

# Characters a page title must never contain raw. In an attribute a bare "&"
# needs escaping; in <title> text it does not, and leaving "&amp;" there means
# anything that regex-extracts the title without decoding sees the entity.
TITLE_ENTITY = re.compile(r"&(?:amp|quot|apos|lt|gt|nbsp|mdash|ndash|hellip|#\d+);")

# An email address immediately followed by a separator and a bare token:
# "demo@autobrainservice.app / demo", "a@b.com: hunter2". The second group must
# not be another address ("sales@x.com · ask for access") and must not be a tag,
# attribute or quote, so mailto anchors stay clean.
CREDENTIAL_LITERAL = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"   # the address
    r"\s*(?:/|\||·|:|—|–|-)\s*"                # "...and the password is"
    r"(?![A-Za-z0-9._%+-]+@)"                          # not another address
    r"(?![<{&\"'])"                                  # not a tag / attribute
    r"([A-Za-z0-9][A-Za-z0-9._!#$%*-]{2,})"           # the secret
)


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
    elif TITLE_ENTITY.search(title):
        bad.append(
            f"title contains a raw HTML entity: {title!r} "
            f"(use a plain '&', not '&amp;')"
        )

    desc = first_group(r'<meta name="description" content="([^"]*)"', text, re.I)
    if not desc:
        bad.append("no meta description")
    elif len(desc) < DESC_MIN:
        bad.append(
            f"description {len(desc)} chars (min {DESC_MIN}) - Google writes "
            f"the snippet itself: {desc!r}"
        )
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

    # The other direction: the sitemap is a list of pages to index, so anything
    # in it that is noindex, a feed, or missing on disk is dead or contradictory
    # weight handed to the crawler.
    stale = []
    for path in sorted(listed):
        target = ROOT / ("index.html" if path == "" else path)
        if path in NON_HTML:
            stale.append(f"{path} -> not an HTML page (drop it from sitemap.xml)")
        elif not target.exists():
            stale.append(f"{path} -> no such file")
        elif is_noindex(target.read_text(encoding="utf-8", errors="ignore")):
            stale.append(f"{path} -> noindex but listed in sitemap.xml")

    return missing, stale, len(listed)


def check_credentials():
    """Every page is scanned, not just indexable ones — a noindex page still
    serves its source to anyone who requests it."""
    bad = []
    for path in html_files():
        text = (ROOT / path).read_text(encoding="utf-8", errors="ignore")
        for m in CREDENTIAL_LITERAL.finditer(text):
            line = text[:m.start()].count("\n") + 1
            bad.append(f"{path}:{line} credential-shaped literal: {m.group(0)!r}")
    return bad

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

    missing, stale, listed = check_sitemap()
    for path in missing:
        violations.append(f"{path}: indexable but not in sitemap.xml")
    for note in stale:
        violations.append(f"sitemap.xml: {note}")

    for hit in check_credentials():
        violations.append(f"published credential: {hit}")

    if violations:
        print("on-page SEO violations:\n")
        for v in violations:
            print(f"  {v}")
        print(f"\n{len(violations)} violation(s). sitemap.xml has {listed} entries.")
        return 1

    print(f"OK: {len(html_files())} pages clean — titles <= {TITLE_MAX} and "
          f"entity-free, descriptions {DESC_MIN}..{DESC_MAX} chars, hreflang "
          f"complete, no broken links, no published credentials, sitemap has "
          f"{listed} indexable entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
