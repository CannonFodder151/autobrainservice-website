# SEO Keyword Targets & Content Brief (AUT-3576)

> Owner: CMO · 2026-10-04 · autobrainservice.app, 55 indexable pages
> Companions: `docs/seo-review.md` (2026-09-28), `docs/SEO-AUDIT-2026-09-30.md`

## 1. Method — and what this brief deliberately leaves out

No search-volume numbers. We have no Keyword Planner, no Search Console and no
data vendor, and every SEO pass so far has been done by hand. Rather than invent
volumes, this brief ranks targets by **intent quality against what AutoBrain can
actually convert**: does the searcher own a car, does the query match a feature
we already ship, can we answer it better than a garage forum. Where a volume
estimate would normally sit, the intent class sits instead.

On-page limits are not negotiable — `scripts/check_seo_pages.py` fails the build
on: title ≤ 60, description 70–160, **unique title and unique description across
all indexable pages**, canonical, `og:` + `twitter:`, hreflang `en-AU` +
`x-default`, every internal href resolving, and sitemap coverage both ways.

## 2. Target map

**Tier 1 — head terms we already hold. Defend, do not duplicate.**

| Query family | Page we hold it on | Intent | Verdict |
|---|---|---|---|
| car maintenance app / tracker (AU) | `index.html`, `features.html` | commercial | Over-served — cluster A |
| rego lookup australia | `blog/free-rego-lookup-australia.html` | transactional | Hold |
| car service / oil change / mechanic prices (AU) | 3 cost posts | informational | Hold; extend with the stranded posts |
| digital car logbook AU | `blog/digital-car-logbook-australia.html` | transactional | Hold |
| petrol prices (WA, QLD) | `petrol-price-map.html` | transactional | Hold, geography-limited |

**Tier 2 — mid-tail we own but split across pages:** the Ownership Advisor launch
(cluster B), the maintenance-app comparison set (cluster A), Home Assistant
(cluster C).

**Tier 3 — net-new, product-owned, buyer intent.** Empty today, and these are the
queries that convert. Three briefs in §4, all on the Ownership Advisor funnel.

## 3. Cannibalisation findings

**Cluster A — three pages for "best car maintenance tracker app Australia"**

| Page | Title | Words |
|---|---|---|
| `blog/best-car-maintenance-app-australia-2026.html` | Best Car Maintenance App Australia 2026 | 408 |
| `blog/best-car-maintenance-tracker-apps.html` | Best Car Maintenance Tracker Apps Australia 2026 | 632 |
| `blog/top-5-car-maintenance-trackers.html` | Top 5 Car Maintenance Trackers Worth Your Money | 757 |

Published 6–21 Aug, all listicle intent, same query family. Google indexes one
and the other two earn nothing. The uniqueness guard cannot catch this — the
titles differ by a word.

*Remediation:* keep `best-car-maintenance-tracker-apps.html` as canonical (longest,
and internal links already point at it). 301 the other two through an Azure SWA
`routes[].redirect` entry and drop them from `sitemap.xml`.

**Cluster B — two "Ownership Advisor is live" launch posts**

- `blog/ownership-advisor-live.html` — "AutoBrain Ownership Advisor — Now Live", published 5 Sep, 841 words.
- `blog/ownership-advisor-coming-soon.html` — title says "Now Live", slug says
  `coming-soon`, body reads "Published 4 September 2026 … shipped on 5 September
  2026. Read the launch post →". A slug that contradicts its own content is a
  quality-signal problem on its own.

*Remediation:* redirect `ownership-advisor-coming-soon.html` →
`ownership-advisor-live.html`.

**Cluster C — Home Assistant intent drift.** `…home-assistant-integration.html`
("is coming", 4 Sep), `…part-2.html` ("how it actually behaves", 6 Sep) and
`ha-coming-soon.html` ("Coming Soon") all coexist. If the integration shipped the
"coming" pages are stale; if it did not, part-2 is claiming behaviour that does
not exist. **Product status confirmation required before any edit.**

## 4. Net-new content briefs — the Ownership Advisor buyer funnel

Three distinct intents, one cluster, all funnelling to `ownership-advisor.html`.
Lengths verified against the CI guard.

**Brief 1 — pillar, commercial investigation**
- Slug `blog/what-is-my-car-worth-australia.html`
- Title (42) `What Is My Car Worth Australia? 2026 Guide`
- Description (155) `What is my car worth in Australia? AutoBrain's Ownership Advisor prices your car from service history, kilometres and condition — no email, no dealer call.`
- H1 `What Is My Car Worth in Australia?`
- Outline: what a valuation actually needs (service history, km, condition, region) → why book value ≠ private-sale price → how the six Ownership Advisor modules price a car → trade-in vs private sale → FAQ
- Links: inbound from `ownership-advisor.html`; outbound to briefs 2 and 3. Register in `blog.html`, `rss.xml`, `sitemap.xml`.

**Brief 2 — decision, mid-funnel**
- Slug `blog/should-i-sell-my-car.html`
- Title (38) `Should I Sell My Car? A Decision Guide`
- Description (154) `Should I sell my car or keep it? Run the repair-vs-replace maths with AutoBrain: repair costs, depreciation, fuel and rego, then decide with real numbers.`
- H1 `Should I Sell My Car, or Keep It?`
- Outline: the repair-vs-replace rule → depreciation by age → when a repair is a write-off → the keep/sell module → FAQ

**Brief 3 — transactional, long-tail**
- Slug `blog/sell-my-car-privately-australia.html`
- Title (57) `Sell My Car Privately Australia: Fees, Paperwork, Pricing`
- Description (152) `Selling a car privately in Australia: paperwork, transfer costs, pricing and where a valuation fits. AutoBrain's Ownership Advisor walks the whole path.`
- H1 `How to Sell Your Car Privately in Australia`
- Outline: paperwork by state → transfer costs → pricing off a valuation → meeting buyers safely → the sell module → FAQ

No `&` in any title: the guard rejects HTML entities, and a raw ampersand is
serialised as one.

## 5. Deferred — not approved for build

- **"Car parts lookup by rego"** — `docs/positioning.md` claims rego lookup
  auto-suggests fitting parts. No page ships that; site copy says receipt and
  parts *scanning* plus inventory. Confirm with the CTO before writing copy that
  promises it.
- **National petrol-price page** — `petrol-price-map.html` covers WA and QLD
  only; a national page needs coverage we do not have data for.
- **HA integration landing page** — blocked on cluster C.

## 6. Implementation order, once approved

1. Cluster A + B redirects. No new content, biggest ranking win.
2. Brief 1 pillar, then briefs 2 and 3 in the same PR.
3. Run `python3 scripts/check_seo_pages.py` locally before push.

## 7. Measurement

Search Console impressions and average position for the three new URLs at 30/60/90
days; internal-link coverage per new page (the guard enforces it); click-through
from `blog.html`. Success is the cluster ranking as one URL instead of three.

---

Approval is approval-gated: the full brief is posted to Discord `#marketing`
under AUT-3576. No page is written and no redirect is shipped before the human
CMO signs off there.