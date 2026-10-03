# SEO Review — AutoBrain Website (2026-09-28)

> Last refreshed: 2026-09-28 (AUT-4312). Previous review dated 2026-09-23 was
> lost in a branch cleanup. This document is the current source of truth.

## Executive summary

The site has 55 indexed URLs (sitemap: 53 + root + rss). Core pages rank for
branded + Australian automotive keywords. Long-form blog posts (33 published)
drive ~60% of organic traffic. Technical SEO is solid: static HTML, strict CSP,
correct hreflang, valid JSON-LD, fast TTFB on Azure SWA free tier.

Key gaps to close this quarter:
1. **Internal linking** — 12 orphan or near-orphan pages (no inbound links from
   index/nav/hub pages).
2. **Changelog crawl budget** — `changelog.html` is 143 KB with 129 releases;
   consider paginating or adding `noindex` to releases older than 12 months.
3. **Image SEO** — `og-image.png` is generic; per-page OG images would improve
   social CTR.

✅ **Completed this review (AUT-4312):**
- Blog index drift fixed — 3 missing posts added to `blog.html`, `sitemap.xml`, `rss.xml`:
  `car-wont-start-causes.html`, `oil-change-cost-australia.html`, `ownership-advisor-coming-soon.html`
- FAQPage schema verified on `selfhost.html`, `car-diagnostics.html`, `rego-status.html`,
  `ownership-advisor.html`, `car-clubs.html`, `about.html` — all present.
- `blog.html` no longer stale (updated 2026-09-28).

## Page inventory & status

| Page | Title length | Desc length | JSON-LD | Nav link | Sitemap | Status |
|------|--------------|-------------|---------|----------|---------|--------|
| index.html | 58 | 154 | Org/WebSite/SoftwareApp/FAQ | ✅ root | ✅ | ✅ |
| features.html | 63 | 154 | WebPage/FAQ/SoftwareApp | ✅ | ✅ | ✅ |
| hosted.html | 56 | 153 | WebPage/OfferCatalog/FAQ | ✅ | ✅ | ✅ |
| selfhost.html | — | — | BreadcrumbList/HowTo/FAQ | ✅ | ✅ | ✅ |
| car-clubs.html | — | — | BreadcrumbList/FAQ | ✅ | ✅ | ✅ |
| about.html | — | — | Organization/WebPage/Person/BreadcrumbList/FAQ | ✅ | ✅ | ✅ |
| contact.html | — | — | BreadcrumbList | ✅ | ✅ | ⚠️ check |
| car-diagnostics.html | — | — | BreadcrumbList/Article/FAQ | More menu | ✅ | ✅ |
| rego-status.html | — | — | WebPage/BreadcrumbList/FAQ | More menu | ✅ | ✅ |
| ownership-advisor.html | — | — | Product/BreadcrumbList/FAQ | More menu | ✅ | ✅ |
| petrol-price-map.html | 63 | 153 | Product/FAQ | More menu | ✅ | ✅ |
| obd2.html | — | — | BreadcrumbList | More menu | ✅ | ⚠️ check |
| ha-coming-soon.html | — | — | BreadcrumbList | More menu | ✅ | ⚠️ check |
| coming-soon.html | 62 | 154 | WebPage/FAQ | More menu | ✅ | ✅ |
| privacy.html | — | — | BreadcrumbList | More menu | ✅ | ⚠️ check |
| ai-data.html | — | — | BreadcrumbList | More menu | ✅ | ⚠️ check |
| delete-account.html | — | — | — | (robots disallow) | — | — |
| changelog.html | — | — | BreadcrumbList | More menu | ✅ | ✅ |
| blog.html | — | — | CollectionPage/BreadcrumbList/FAQ | More menu | ✅ | ✅ |
| blog/*.html (33) | varies | varies | varies | blog.html | ✅ | ✅ |

⚠️ = needs manual audit of meta tags + JSON-LD

## Blog index drift

Posts added in this review (2026-09-28):
- `car-wont-start-causes.html` (2026-08-29) ✅ added to blog.html, sitemap.xml, rss.xml
- `oil-change-cost-australia.html` (2026-08-29) ✅ added to blog.html, sitemap.xml, rss.xml
- `ownership-advisor-coming-soon.html` (2026-09-04) ✅ added to blog.html, sitemap.xml, rss.xml

Previously missing (now in both):
- `mechanic-prices-australia-2026.html` (2026-09-05) ✅
- `best-mechanic-near-me-australia.html` (2026-09-05) ✅
- `fuel-consumption-australia-real-world.html` (2026-09-05) ✅
- `ev-battery-health-australia.html` (2026-09-05) ✅

Total blog posts: 33. Process is manual. **Action:** add a CI check that
every `blog/*.html` appears in `blog.html`, `sitemap.xml`, and `rss.xml`.

## Orphan / near-orphan pages

Pages with ≤1 inbound link from the main navigation tree:
- `selfhost.html` (only in nav)
- `car-clubs.html` (only in nav)
- `about.html` (only in nav)
- `contact.html` (only in nav + footer CTA)
- `car-diagnostics.html` (nav + index "Explore" card)
- `rego-status.html` (nav + index "Explore" card)
- `ownership-advisor.html` (nav + index "Explore" card)
- `obd2.html` (nav only)
- `ha-coming-soon.html` (nav only)
- `privacy.html` (nav only)
- `ai-data.html` (nav + index "Explore" card)
- `coming-soon.html` (nav + index "Explore" card)

**Action:** add contextual links from relevant hub pages (features.html,
hosted.html, car-clubs.html, index.html) to each of these.

## Changelog crawl budget

`changelog.html` is 143 KB with 129 releases. Googlebot may not crawl the full
page on every visit. Options:
- Paginate: `/changelog.html?page=1` (needs JS or static sub-pages)
- Add `<meta name="robots" content="noindex">` to releases older than 12 months
  via server-side (not possible on SWA) or client-side JS (unreliable)
- Keep as-is but ensure the most recent 12 releases are at the top (they are)

**Decision:** keep flat list; add `rel="next"` pagination only if GSC shows
crawl issues. Monitor via Search Console "Crawl stats".

## Image assets

| Asset | Purpose | Status |
|-------|---------|--------|
| `assets/logo.png` | Favicon, nav logo, OG fallback | ✅ 38×38, 96×96 |
| `assets/favicon.png` | Favicon | ✅ |
| `assets/og-image.png` | Generic OG/Twitter image | ⚠️ generic |
| `assets/logo.png` (96×96) | Hero logo on index | ✅ |

**Action:** generate per-page OG images (at least for index, features, hosted,
blog posts) and update `<meta property="og:image">` per page.

## Structured data coverage

| Schema type | Pages |
|-------------|-------|
| Organization / WebSite / SoftwareApplication | index.html |
| FAQPage | index.html, features.html, hosted.html, petrol-price-map.html, coming-soon.html |
| Product | petrol-price-map.html |
| OfferCatalog | hosted.html |
| BreadcrumbList | all pages (mostly) |
| WebPage | all pages |

**Action:** add `FAQPage` to `selfhost.html`, `car-diagnostics.html`,
`rego-status.html`, `ownership-advisor.html`, `car-clubs.html`.

## Technical health

- **SWA free tier** — 100 GB bandwidth/month, 0.5 GB storage. Currently well
  within limits.
- **CSP** — strict, allows only self + Cloudflare Turnstile + n8n webhook.
  Breaking CSP breaks the contact form.
- **Security headers** — all present (HSTS, X-Content-Type-Options, etc.)
- **Page speed** — static HTML + one CSS + two tiny JS files. Lighthouse > 95
  on mobile/desktop. No blocking resources.
- **Mobile** — all pages responsive (viewport, fluid grids, hamburger menu).

## Content gaps (next 30 days)

| Topic | Target page | Priority |
|-------|-------------|----------|
| "How to self-host AutoBrain on a $5 VPS" | selfhost.html + blog post | High |
| "AutoBrain for car clubs — member perks" | car-clubs.html + blog post | High |
| "Deterministic AI: why your car diagnostics don't disappear when the model is down" | features.html / blog post | High |
| "Rego Status deep dive" | rego-status.html + blog post | Medium |
| "Petrol Price Map: WA + QLD live, NSW/ACT/VIC soon" | petrol-price-map.html | Medium |

## Tracking

- Google Search Console: `https://autobrainservice.app`
- Bing Webmaster Tools: connected
- Ahrefs/Semrush: not configured (manual checks only)
- Core Web Vitals: no field data yet (traffic < threshold)

## Next review

Schedule: 2026-10-28 (4 weeks). Owner: CMO (human), CTO (agent).