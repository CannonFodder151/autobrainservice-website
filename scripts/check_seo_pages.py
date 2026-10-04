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

Plus uniqueness across pages, because a per-page check cannot see its
neighbours (added after the AUT-5339 audit of all 55 pages):

  title        unique across indexable pages
  description  unique across indexable pages   - two pages sharing a title or a
                                               description compete for the same
                                               keyword; Google indexes one and
                                               the other earns nothing

Plus site-level integrity, which is where the 404s came from:

  every internal href resolves to a file that exists
  sitemap.xml covers every indexable page
  sitemap.xml lists only indexable pages   - a noindex URL or a feed (rss.xml)
                                              in the sitemap sends mixed signals
                                              and wastes crawl budget

And one security invariant, added after AUT-5045 (a shared demo password was
published in cleartext on an indexable page):

  no email address is followed by a password-shaped literal

Plus FAQ parity, added after AUT-5425 (the QA review of the AUT-5326
posts found the FAQPage JSON-LD questions had drifted from the rendered
<details> accordion — Google expects marked-up FAQ content to match the
visible FAQ):

  FAQPage mainEntity[].name set == <details><summary> text set

The comparison is exact after whitespace normalisation: near-duplicates
are real defects here, not audit findings, because the markup and the
rendered accordion are two renderings of the same questions. Only pages
that render an accordion are checked — a page with FAQPage markup and
no <details> at all has no visible FAQ to mirror (that is a separate
audit finding, tracked as a follow-up, not a parity failure).

The uniqueness rule was added after AUT-5339: the audit that re-checked all
55 pages found the per-page invariants holding, but could not see that
ownership-advisor.html and blog/ownership-advisor-live.html shipped the same
description, which is exactly the defect a per-page check is blind to.

The description floor and the sitemap-hygiene rules were added after AUT-5325.
The audit behind it ran against a stale checkout: the three thin descriptions
it reported have since been rewritten by earlier passes, and no floor existed
to hold them there. The title-entity and sitemap defects were live on main.

Exit 0 = clean. Exit 1 = violations, listed.

Override a limit with an env var when a page genuinely needs more:
  SEO_TITLE_MAX, SEO_DESC_MAX, SEO_DESC_MIN
"""
import json
import os
import re
import sys
from collections import defaultdict
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


def indexable_pages():
    """Pages the page-level invariants apply to.

    noindex pages are exempt: teaser and legacy posts are deliberately
    near-copies of the live page, and AUT-5325 parked them with noindex rather
    than pretending the duplication does not exist.
    """
    return [
        p for p in html_files()
        if p not in EXEMPT
        and not is_noindex((ROOT / p).read_text(encoding="utf-8", errors="ignore"))
    ]


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


def check_duplicates():
    """Group indexable pages by title and by description.

    Whitespace is normalised and case folded so the same string cannot
    reappear through a stray space or capital. Exact matches only: a
    fuzzy threshold would only manufacture false positives, and
    near-duplicates are an audit finding, not a guard.
    """
    titles = defaultdict(list)
    descriptions = defaultdict(list)
    for path in indexable_pages():
        text = (ROOT / path).read_text(encoding="utf-8", errors="ignore")
        title = " ".join(first_group(r"<title>(.*?)</title>", text).split())
        desc = " ".join(
            first_group(r'<meta name="description" content="([^"]*)"', text, re.I).split()
        )
        if title:
            titles[title.casefold()].append((path, title))
        if desc:
            descriptions[desc.casefold()].append((path, desc))

    bad = []
    for label, groups in (("title", titles), ("description", descriptions)):
        for value, pages in sorted(groups.items()):
            if len(pages) > 1:
                names = ", ".join(p for p, _ in pages)
                shown = pages[0][1]
                bad.append(
                    f"duplicate {label} on {len(pages)} pages ({names}): "
                    f"{shown[:70]!r}"
                )
    return bad


def strip_tags(text):
    return " ".join(re.sub(r"<[^>]+>", "", text).split())


def faqpage_questions(text):
    """Question strings from a page's FAQPage JSON-LD, in document order.

    The block is usually a bare object but the blog posts nest it inside
    an @graph, so both shapes are handled. Unparseable JSON is skipped
    rather than raised: a broken JSON-LD block is a rendering defect, not
    a parity finding, and this check is only about question parity.
    """
    questions = []
    for m in re.finditer(
        r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', text, re.S
    ):
        try:
            data = json.loads(m.group(1))
        except ValueError:
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        for node in nodes:
            if isinstance(node, dict) and node.get("@type") == "FAQPage":
                for q in node.get("mainEntity", []):
                    questions.append(strip_tags(q.get("name", "")))
    return questions


def accordion_questions(text):
    """Question strings from the rendered <details><summary> FAQ accordion."""
    return [
        strip_tags(m.group(1))
        for m in re.finditer(
            r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>", text, re.S
        )
    ]


def check_faq_parity():
    """Every indexable page that renders an FAQ accordion must mark up the
    same questions in its FAQPage JSON-LD.

    Found by QA on AUT-5425: the three AUT-5326 posts shipped FAQPage
    JSON-LD whose questions had drifted from the accordion, so the markup
    and the visible FAQ were two different sets of questions.

    Pages with no accordion are skipped. There is nothing rendered to
    mirror, and flagging them would make this check a proxy for the
    separate "FAQPage markup with no visible FAQ" audit.
    """
    bad = []
    for path in indexable_pages():
        text = (ROOT / path).read_text(encoding="utf-8", errors="ignore")
        rendered = accordion_questions(text)
        if not rendered:
            continue
        marked = faqpage_questions(text)
        marked_set, rendered_set = set(marked), set(rendered)
        if marked_set == rendered_set:
            continue

        if not marked:
            bad.append(
                f"{path}: {len(rendered)} FAQ questions in the accordion but no "
                f"FAQPage JSON-LD to mirror them"
            )
            continue
        for q in sorted(rendered_set - marked_set):
            bad.append(f"{path}: accordion question not in FAQPage JSON-LD: {q!r}")
        for q in sorted(marked_set - rendered_set):
            bad.append(f"{path}: FAQPage JSON-LD question not in the accordion: {q!r}")
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

    for path in indexable_pages():
        for issue in check_page(path):
            violations.append(f"{path}: {issue}")

    for dup in check_duplicates():
        violations.append(f"keyword cannibalisation: {dup}")

    for link in check_links():
        violations.append(f"broken internal link: {link}")

    missing, stale, listed = check_sitemap()
    for path in missing:
        violations.append(f"{path}: indexable but not in sitemap.xml")
    for note in stale:
        violations.append(f"sitemap.xml: {note}")

    for hit in check_credentials():
        violations.append(f"published credential: {hit}")

    for faq in check_faq_parity():
        violations.append(f"FAQPage/accordion parity: {faq}")

    if violations:
        print("on-page SEO violations:\n")
        for v in violations:
            print(f"  {v}")
        print(f"\n{len(violations)} violation(s). sitemap.xml has {listed} entries.")
        return 1

    print(f"OK: {len(html_files())} pages clean — titles <= {TITLE_MAX} and "
          f"entity-free, descriptions {DESC_MIN}..{DESC_MAX} chars, titles and "
          f"descriptions unique across pages, hreflang complete, no broken "
          f"links, no published credentials, FAQPage JSON-LD matches every "
          f"rendered FAQ accordion, sitemap has {listed} indexable entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
