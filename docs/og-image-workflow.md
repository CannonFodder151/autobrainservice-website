# OG Image Generation Workflow

## Overview

AutoBrain generates per-post OG images for each blog post, replacing the previous approach where all posts shared a single generic `assets/og-image.png`. The per-post OG images improve social share preview quality on Twitter/X, LinkedIn, Facebook, and other platforms that consume the `og:image` meta tag.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Blog post  │────▶│ Section mapping  │────▶│  accent overlay   │
│  metadata   │     │ (article:section)│     │  (color per section)│
└─────────────┘     └──────────────────┘     └────────────────────┘
                                                         │
                                                         ▼
                                              ┌────────────────────┐
                                              │  Final OG image    │
                                              │  1200×630px PNG    │
                                              │  assets/og-*.png   │
                                              └────────────────────┘
```

## Pipeline Steps

1. **Source template** — A base OG image template (1200×630px) contains the AutoBrain logo, blog title area, and a tinted accent band.
2. **Section lookup** — The `article:section` meta tag value from the blog post's `<head>` determines which accent color to apply.
3. **Accent overlay** — The accent color is composited onto the template as a top or bottom band.
4. **Output file** — The composited image is saved to `assets/og-{slug}.png` (or `assets/og-{section-slug}.png` for section-wide images).
5. **Meta injection** — The `<head>` of each blog post HTML file receives updated meta tags:
   - `og:image` → `https://autobrainservice.app/assets/og-{slug}.png`
   - `og:image:width` → `1200`
   - `og:image:height` → `630`
   - `twitter:image` → same path

## Section-to-Accent-Color Mapping

| `article:section` value | Section slug | Accent color | Hex (approx.) |
|--------------------------|--------------|--------------|----------------|
| AI & Technology | `ai-tech` | Electric blue | `#2563EB` |
| Announcements | `announcements` | Orange | `#F59E0B` |
| Car clubs | `car-clubs` | Teal | `#0D9488` |
| Data ownership | `data-ownership` | Indigo | `#6366F1` |
| Diagnostics | `diagnostics` | Red | `#DC2626` |
| Engineering | `engineering` | Gray | `#6B7280` |
| EV & Battery | `ev-battery` | Green | `#16A34A` |
| Features | `features` | Blue | `#3B82F6` |
| Fuel & Cost | `fuel-cost` | Amber | `#D97706` |
| Fuel & Cost Tracking | `fuel-cost-tracking` | Amber | `#D97706` |
| Guides | `guides` | Purple | `#8B5CF6` |
| Integrations | `integrations` | Cyan | `#06B6D4` |
| Maintenance | `maintenance` | Orange-red | `#EA580C` |
| Ownership | `ownership` | Deep purple | `#7C3AED` |
| Ownership Costs | `ownership-costs` | Pink | `#EC4899` |
| Product | `product` | Teal | `#14B8A6` |
| Reliability | `reliability` | Emerald | `#10B981` |
| Troubleshooting | `troubleshooting` | Yellow | `#EAB308` |
| Workshops | `workshops` | Slate | `#475569` |

> **TODO for CMO:** Verify each hex color matches the brand palette. Current values are approximate and based on the dark theme accent conventions. Update this table when the final color tokens are confirmed.

## Current Blog Posts and Sections

| Blog post file | `article:section` |
|----------------|-------------------|
| `ai-that-works-even-when-the-ai-is-down.html` | Reliability |
| `android-app-full-release.html` | Announcements |
| `autobrain-app-tour.html` | Guides |
| `autobrain-for-car-clubs.html` | Car clubs |
| `autobrain-home-assistant-integration.html` | Integrations |
| `best-car-maintenance-app-australia-2026.html` | Maintenance |
| `best-car-maintenance-tracker-apps.html` | Maintenance |
| `best-mechanic-near-me-australia.html` | Workshops |
| `car-dashboard-warning-lights-australia.html` | Maintenance |
| `car-fuel-tracker-app-australia.html` | Fuel & Cost Tracking |
| `car-service-cost-australia.html` | Ownership Costs |
| `car-wont-start-causes.html` | Troubleshooting |
| `check-engine-light-australia-obd2-codes-2026.html` | Diagnostics |
| `community-garage-ga.html` | Announcements |
| `digital-car-logbook-australia.html` | Features |
| `ev-battery-health-australia.html` | EV & Battery |
| `free-rego-lookup-australia.html` | Features |
| `fuel-consumption-australia-real-world.html` | Fuel & Cost |
| `have-you-ever-repair-bill.html` | Features |
| `issues-blog.html` | Announcements |
| `obd2-code-reader-app-australia.html` | Diagnostics |
| `oil-change-cost-australia.html` | Ownership Costs |
| `ownership-advisor-coming-soon.html` | Ownership |
| `predictive-maintenance-car-ai-diagnostics.html` | AI & Technology |
| `top-5-car-maintenance-trackers.html` | Maintenance |
| `what-is-autobrain.html` | Product |
| `what-our-obd2-adapter-will-do.html` | Announcements |
| `why-a-simpler-stack-is-a-better-stack.html` | Engineering |
| `workshop-management-software-australian-mechanics.html` | Workshops |
| `your-data-your-way.html` | Data ownership |

## Meta Tag Pattern

Each blog post `<head>` includes:

```html
<meta property="og:image" content="https://autobrainservice.app/assets/og-{slug}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://autobrainservice.app/assets/og-{slug}.png">
```

The `{slug}` matches the blog post filename without `.html`, or the section slug for section-wide OG images.

## File Locations

- **Source template**: `assets/og-image.png` (1200×630, generic fallback)
- **Per-post images**: `assets/og-{slug}.png` (one per blog post, if per-post images are generated)
- **Section images**: `assets/og-section-{section-slug}.png` (one per section, if section-wide images are used)

## Notes

- The generic `assets/og-image.png` (1200×400) is retained as a fallback for pages without a specific OG image (about.html, features.html, etc.).
- All OG images use the 1200×630 aspect ratio for maximum compatibility across social platforms.
- The `twitter:card` type `summary_large_image` is used throughout to ensure the OG image renders prominently on X/Twitter.
