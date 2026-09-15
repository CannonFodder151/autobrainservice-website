# Person Author Bio Schema

## Overview

AUT-3115 introduces a `schema.org/Person` structured data block on all 33 AutoBrain blog posts, replacing the previous approach where blog post authors were marked as `{ "@type": "Organization", "name": "AutoBrain" }`. The Person schema improves Google's understanding of article authorship and can trigger enhanced author bylines in search results.

The Person schema for Nathan already exists on `about.html` and is the canonical source. AUT-3115 replicates the same structured data into each blog post's `<script type="application/ld+json">` block.

## Person Schema Fields

The following `schema.org/Person` fields are used across all blog posts:

| Field | Type | Value | Description |
|-------|------|-------|-------------|
| `@type` | `string` | `"Person"` | Schema.org type identifier |
| `@id` | `URL` | `https://autobrainservice.app/#nathan` | Canonical person identifier (same as about.html) |
| `name` | `string` | `"Nathan"` | Author display name |
| `jobTitle` | `string` | `"IT professional and software developer"` | Professional role |
| `worksFor` | `@id` ref | `{ "@id": "https://autobrainservice.app/#org" }` | Reference to the Organization |
| `knowsAbout` | `array<string>` | `["infrastructure", "networking", "software development", "car maintenance", "vehicle restoration"]` | Expertise areas |

## JSON-LD Example

Every blog post includes this structured data in the `<head>`:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Article",
      "headline": "Blog post title",
      "description": "Post description",
      "author": { "@id": "https://autobrainservice.app/#nathan" },
      "publisher": {
        "@type": "Organization",
        "@id": "https://autobrainservice.app/#org",
        "name": "AutoBrain",
        "logo": { "@type": "ImageObject", "url": "https://autobrainservice.app/assets/logo.png" }
      },
      "datePublished": "2026-MM-DD",
      "dateModified": "2026-MM-DD",
      "mainEntityOfPage": "https://autobrainservice.app/blog/{slug}.html",
      "image": "https://autobrainservice.app/assets/og-{slug}.png"
    },
    {
      "@type": "Person",
      "@id": "https://autobrainservice.app/#nathan",
      "name": "Nathan",
      "jobTitle": "IT professional and software developer",
      "worksFor": { "@id": "https://autobrainservice.app/#org" },
      "knowsAbout": ["infrastructure", "networking", "software development", "car maintenance", "vehicle restoration"]
    },
    {
      "@type": "Organization",
      "@id": "https://autobrainservice.app/#org",
      "name": "AutoBrain",
      "url": "https://autobrainservice.app/",
      "logo": { "@type": "ImageObject", "url": "https://autobrainservice.app/assets/logo.png" }
    }
  ]
}
```

## Key Design Decisions

### Why `@id` references instead of inline objects

The `author` field on the Article uses `{ "@id": "https://autobrainservice.app/#nathan" }` rather than duplicating the Person object. This:
- Keeps the Person definition authoritative in one place (the `@graph` block)
- Makes it trivial to update author fields across all posts (change the Person in `@graph`)
- Avoids Google seeing conflicting Person data across pages

### Canonical Person URI

`https://autobrainservice.app/#nathan` is the canonical `@id` for Nathan across the site. It matches the Person definition already present in `about.html` (lines 45–51). Google uses this URI to associate blog posts with the same author entity.

### Organization reference

The `worksFor` field on the Person uses `{ "@id": "https://autobrainservice.app/#org" }` to reference the Organization, reinforcing the employer–employee relationship in structured data.

## Data Source Mapping

The Person schema fields derive from the canonical Person definition in `about.html`:

```html
<!-- from about.html @graph block -->
{
  "@type": "Person",
  "@id": "https://autobrainservice.app/#nathan",
  "name": "Nathan",
  "jobTitle": "IT professional and software developer",
  "worksFor": { "@id": "https://autobrainservice.app/#org" },
  "knowsAbout": [
    "infrastructure",
    "networking",
    "software development",
    "car maintenance",
    "vehicle restoration"
  ]
}
```

## Blog Post Coverage

AUT-3115 applies this Person schema to all 33 blog posts:

| Blog post file | Status |
|----------------|--------|
| `ai-that-works-even-when-the-ai-is-down.html` | Requires update (currently uses Organization) |
| `android-app-full-release.html` | Requires update |
| `autobrain-app-tour.html` | Requires update |
| `autobrain-for-car-clubs.html` | Requires update |
| `autobrain-home-assistant-integration.html` | Requires update |
| `best-car-maintenance-app-australia-2026.html` | Requires update |
| `best-car-maintenance-tracker-apps.html` | Requires update |
| `best-mechanic-near-me-australia.html` | Requires update |
| `car-dashboard-warning-lights-australia.html` | Requires update |
| `car-fuel-tracker-app-australia.html` | Requires update |
| `car-service-cost-australia.html` | Requires update |
| `car-wont-start-causes.html` | Requires update |
| `check-engine-light-australia-obd2-codes-2026.html` | Requires update |
| `community-garage-ga.html` | Requires update |
| `digital-car-logbook-australia.html` | Requires update |
| `ev-battery-health-australia.html` | Requires update |
| `free-rego-lookup-australia.html` | Requires update |
| `fuel-consumption-australia-real-world.html` | Requires update |
| `have-you-ever-repair-bill.html` | Requires update |
| `issues-blog.html` | Requires update |
| `obd2-code-reader-app-australia.html` | Requires update |
| `oil-change-cost-australia.html` | Requires update |
| `ownership-advisor-coming-soon.html` | Requires update |
| `predictive-maintenance-car-ai-diagnostics.html` | Requires update |
| `top-5-car-maintenance-trackers.html` | Requires update |
| `what-is-autobrain.html` | Requires update |
| `what-our-obd2-adapter-will-do.html` | Requires update |
| `why-a-simpler-stack-is-a-better-stack.html` | Requires update |
| `workshop-management-software-australian-mechanics.html` | Requires update |
| `your-data-your-way.html` | Requires update |
| `about.html` | Already has Person schema (canonical source) |
| `features.html` | No article author — not applicable |
| `blog.html` | No article author — not applicable |

## Validation

After AUT-3115 is applied, verify with:

1. **Google Rich Results Test** — Paste each blog post URL and confirm the Article schema shows a Person author (not Organization).
2. **Schema.org validator** — Validate the JSON-LD block at `https://validator.schema.org/`.
3. **Search Console** — Monitor "Enhancements > Articles" in Google Search Console for author-related rich result changes.

## Notes

- The `knowsAbout` array is not exhaustive — it represents the primary expertise areas relevant to AutoBrain's domain.
- If a second author is added in the future, add a second `Person` block to the `@graph` and reference it via `{ "@id": "..." }` in the Article's `author` field.
- The `jobTitle` and `knowsAbout` fields are optional but recommended for author knowledge panel eligibility.
