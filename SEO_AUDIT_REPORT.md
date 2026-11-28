# AutoBrain Website SEO Audit Report
**Date:** 2026-11-27  
**Auditor:** SEO Designer Agent  
**Website:** https://autobrainservice.app  
**Repo:** CannonFodder151/autobrainservice-website

---

## Executive Summary

The AutoBrain marketing website has **strong technical SEO foundations** with comprehensive schema markup, unique titles/descriptions across 64 pages, proper hreflang implementation, and a clean sitemap. The automated SEO checker (`scripts/check_seo_pages.py`) passes with 0 violations.

**However, content gaps exist for key product features** that need dedicated landing pages and blog posts to capture search traffic.

---

## Current State Analysis

### ✅ Technical SEO (Passing)
| Check | Status | Details |
|-------|--------|---------|
| Title tags (≤60 chars, no entities) | ✅ Pass | All 64 indexable pages |
| Meta descriptions (70-160 chars) | ✅ Pass | All unique |
| Canonical URLs | ✅ Pass | All pages |
| Open Graph tags | ✅ Pass | All pages |
| Twitter Cards | ✅ Pass | All pages |
| hreflang (en-AU + x-default) | ✅ Pass | All pages |
| Internal link integrity | ✅ Pass | No broken links |
| Sitemap coverage | ✅ Pass | 60 indexable entries |
| FAQPage ↔ Accordion parity | ✅ Pass | All pages |
| No published credentials | ✅ Pass | Clean |
| Coverage-prose parity | ✅ Pass | Status tiles match content |

### 📊 Content Inventory
| Page Type | Count | Status |
|-----------|-------|--------|
| Core pages (index, features, hosted, selfhost, about) | 7 | Complete |
| Feature deep-dives (diagnostics, rego-status, ownership-advisor, etc.) | 8 | Complete |
| Blog posts | 42 | Strong coverage |
| Coming soon / teaser pages | 3 | Noindex (correct) |
| Legal/policy pages | 3 | Complete |
| **Total indexable** | **60** | |

---

## Content Gaps Identified

### 1. Missing Dedicated Feature Pages (High Priority)
| Feature | Current Coverage | Gap |
|---------|------------------|-----|
| **Vehicle Health Score** | Mentioned in predictive maintenance blog post only | No dedicated landing page or feature-specific blog post |
| **Electric Spy** | Mentioned in coming-soon.html and EV battery health blog | No dedicated feature page or deep-dive blog post |
| **PHEV Tracking** | Mentioned in coming-soon.html | No dedicated page or blog post |
| **AI Diagnostics** | Covered in car-diagnostics.html and predictive maintenance blog | Could use a dedicated "AI Diagnostics" feature page |

### 2. Missing Comparison Pages (Medium Priority)
| Competitor Category | Gap |
|---------------------|-----|
| vs. Car Scanner Apps (Torque, Car Scanner ELM OBD2) | No comparison page |
| vs. Maintenance Trackers (myCARFAX, Drivvo, Fuelly) | No comparison page |
| vs. EV Apps (Tesla app, ChargePoint, PlugShare) | No comparison page |
| vs. Fleet/Club Management | No comparison page |

### 3. Missing High-Intent Keyword Pages (Medium Priority)
| Keyword Cluster | Search Intent | Gap |
|-----------------|---------------|-----|
| "vehicle health score app" | Commercial/Informational | No page |
| "electric vehicle charging price tracker Australia" | Commercial | No page |
| "PHEV fuel tracking app Australia" | Commercial | No page |
| "car diagnostic app with AI Australia" | Commercial | Partial (car-diagnostics.html) |
| "best car maintenance app Australia 2026" | Commercial | Covered in blog |

---

## Keyword Opportunities (from ROADMAP.md & MARKETING.md)

### Phase 1 Positioning Keywords
- "car maintenance app that works without AI" (unique positioning)
- "deterministic fallback car diagnostics"
- "open source car maintenance app Australia"
- "self hosted vehicle tracker MIT license"

### Feature-Specific Keywords
- "vehicle health score" → New page needed
- "Electric Spy charging price watch" → New page needed
- "PHEV tracking app Australia" → New page needed
- "EV log book Australia kWh 100km" → Partial (EV battery health blog)
- "servo spy fuel price watch Australia" → Covered in features.html

---

## Recommended Actions (Priority Order)

### 🔴 Critical (Do First)
1. **Create Vehicle Health Score landing page** (`vehicle-health-score.html`) + blog post
2. **Create Electric Spy feature page** (`electric-spy.html`) + blog post
3. **Create PHEV tracking feature page** (`phev-tracking.html`) + blog post
4. **Create AI Diagnostics feature page** (`ai-diagnostics.html`) or enhance car-diagnostics.html

### 🟡 High (Do Next)
5. **Create comparison pages:**
   - `vs-car-scanner-apps.html`
   - `vs-maintenance-trackers.html`
   - `vs-ev-apps.html`
6. **Add analytics/GTM implementation** (check if GA4/GTM is already in place)
7. **Add conversion tracking** for demo signups, waitlist emails, plan selections

### 🟢 Medium (Schedule)
8. **Enhance blog content strategy** with keyword-focused posts
9. **Add more FAQ schema** to high-traffic pages
10. **Review and optimize Core Web Vitals** (check LCP, CLS, INP)

---

## Analytics & Conversion Tracking Status

**Need to verify:**
- [ ] Google Analytics 4 (GA4) implementation
- [ ] Google Tag Manager (GTM) container
- [ ] Conversion events: demo request, waitlist signup, plan selection, contact form
- [ ] Enhanced ecommerce for plan tiers
- [ ] Scroll depth / engagement tracking
- [ ] Search Console property verified

---

## Competitor Content Analysis

### Direct Competitors (Australian Market)
| Competitor | Strengths | Our Advantage |
|------------|-----------|---------------|
| **Car Scanner ELM OBD2** | Large user base, simple | We have predictive maintenance, fuel tracking, rego, logbook |
| **Torque Pro** | Advanced PIDs, customization | We're free/self-hostable, AI diagnostics, deterministic fallbacks |
| **myCARFAX** | Service history, recalls | We add fuel tracking, OBD2, EV features, open source |
| **Drivvo / Fuelly** | Fuel tracking focus | We add full maintenance + diagnostics + EV + PHEV |
| **Tesla App / ChargePoint** | Brand-specific | We're multi-brand, PHEV support, price watch (Electric Spy) |

---

## Next Steps

1. **Create missing feature pages** (4 new HTML pages with full SEO markup)
2. **Write 4 dedicated blog posts** for each feature
3. **Create 3 comparison pages** with structured data
4. **Verify and document analytics implementation**
5. **Add new pages to sitemap.xml**
6. **Run SEO checker** to validate all new pages
7. **Submit new URLs to Google Search Console**

---

## Files to Create/Modify

### New Pages
- `vehicle-health-score.html`
- `electric-spy.html`
- `phev-tracking.html`
- `ai-diagnostics.html` (or enhance car-diagnostics.html)
- `vs-car-scanner-apps.html`
- `vs-maintenance-trackers.html`
- `vs-ev-apps.html`

### New Blog Posts
- `blog/vehicle-health-score-explained.html`
- `blog/electric-spy-charging-price-watch.html`
- `blog/phev-tracking-australia-guide.html`
- `blog/ai-car-diagnostics-how-it-works.html`

### Modified Files
- `sitemap.xml` (add new URLs)
- `blog.html` (add new blog cards)
- `index.html` / `features.html` (link to new feature pages)
- `nav.js` (if new nav items needed)

---

*Report generated by SEO Designer Agent for AUT-970*