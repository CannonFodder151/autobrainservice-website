#!/usr/bin/env python3
import re
import html
from datetime import datetime

SITE = "https://autobrainservice.app"
FEED_TITLE = "AutoBrain Blog"
FEED_DESC = "Practical guides on car maintenance tracking, fuel intelligence, AI diagnostics and smart vehicle ownership — from the team behind AutoBrain."

def parse_date(s):
    """Return a datetime, not the RFC 822 string: sorting the feed on the
    formatted string sorts by weekday name, not by date."""
    for fmt in ("%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            pass
    return datetime(2026, 8, 1)

def rfc822(d):
    return d.strftime("%a, %d %b %Y 00:00:00 +1000")

def main():
    txt = open("blog.html").read()
    cards = re.findall(r"<article class=\"card blog-card u-inherit\">(.*?)</article>", txt, re.DOTALL)
    items = []
    for c in cards:
        date_m = re.search(r"<span class=\"date\">(.*?)</span>", c)
        title_m = re.search(r"<h3><a href=\"(.*?)\">(.*?)</a></h3>", c)
        desc_m = re.search(r"<p>(.*?)</p>", c)
        url = SITE + "/" + (title_m.group(1) if title_m else "")
        title = html.unescape(re.sub(r"<[^>]+>", "", title_m.group(2))) if title_m else ""
        desc = html.unescape(re.sub(r"<[^>]+>", "", desc_m.group(1))) if desc_m else ""
        raw_date = date_m.group(1).split("·")[0].strip() if date_m else ""
        pub_date = parse_date(raw_date)
        guid = SITE + "/" + (title_m.group(1) if title_m else "")
        items.append((pub_date, url, title, desc, guid))

    items.sort(key=lambda x: x[0], reverse=True)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        f"<title>{html.escape(FEED_TITLE)}</title>",
        f"<description>{html.escape(FEED_DESC)}</description>",
        f"<link>{SITE}/blog.html</link>",
        f"<atom:link href=\"{SITE}/rss.xml\" rel=\"self\" type=\"application/rss+xml\" />",
        "<language>en-AU</language>",
        "<lastBuildDate>" + datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000") + "</lastBuildDate>",
    ]
    for pub_date, url, title, desc, guid in items:
        lines.append("<item>")
        lines.append(f"<title>{html.escape(title)}</title>")
        lines.append(f"<description>{html.escape(desc)}</description>")
        lines.append(f"<link>{html.escape(url)}</link>")
        lines.append(f"<guid isPermaLink=\"true\">{html.escape(guid)}</guid>")
        lines.append(f"<pubDate>{rfc822(pub_date)}</pubDate>")
        lines.append("</item>")
    lines += ["</channel>", "</rss>"]

    with open("rss.xml", "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Generated rss.xml with {len(items)} items")

if __name__ == "__main__":
    main()
