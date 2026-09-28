#!/usr/bin/env python3
"""Fail if any blog post is missing from blog.html, sitemap.xml or rss.xml.

Adding a post under blog/ is not enough: the blog index, the sitemap and the RSS
feed are all hand-maintained, and drift there means the post is orphaned and
invisible to search engines and feed readers. This check closes that loop.

Exit 0 = in sync. Exit 1 = drift, with the missing references listed.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def blog_posts():
    return sorted(p.name for p in (ROOT / "blog").glob("*.html"))


def main():
    posts = blog_posts()
    if not posts:
        sys.exit("no posts found under blog/ — wrong working directory?")

    blog_html = (ROOT / "blog.html").read_text()
    sitemap = (ROOT / "sitemap.xml").read_text()
    rss = (ROOT / "rss.xml").read_text()

    missing = []
    for post in posts:
        for label, haystack in (
            ("blog.html", blog_html),
            ("sitemap.xml", sitemap),
            ("rss.xml", rss),
        ):
            if post not in haystack:
                missing.append(f"  {post} -> missing from {label}")

    # A post listed in the index but absent from blog/ is the same bug reversed:
    # a dead link on a page Google crawls.
    indexed = set(re.findall(r'href="blog/([^"]+\.html)"', blog_html))
    for orphan in sorted(indexed - set(posts)):
        missing.append(f"  {orphan} -> listed in blog.html but no such file")

    if missing:
        print("blog index drift:\n" + "\n".join(missing))
        print(f"\n{len(missing)} problem(s) across {len(posts)} posts.")
        return 1

    print(f"OK: {len(posts)} posts present in blog.html, sitemap.xml and rss.xml")
    return 0


if __name__ == "__main__":
    sys.exit(main())
