# AutoBrain Website

Public marketing site for **AutoBrain** — the AI-powered car companion.

**Live:** https://autobrainservice.app
**Demo app:** https://demo.autobrainservice.app

## Hosting

Deployed as an **Azure Static Web App** (free tier) from this private repo. DNS for
`autobrainservice.app` points at the SWA endpoint (see the Azure portal; currently
proxied via Cloudflare).

- App location: `/` (static site, no build step — `skip_app_build: true`)
- Config: [`staticwebapp.config.json`](staticwebapp.config.json) (routing, headers, `.apk` MIME type)
- Deploy workflow: Azure Static Web Apps publish action in [`.github/workflows/azure-static-web-apps-happy-glacier-0f26af910.yml`](.github/workflows/azure-static-web-apps-happy-glacier-0f26af910.yml)
- Requires the Azure SWA deployment-token secret configured in GitHub (set via the Azure portal, "Manage deployment token")

## Changelog (auto-synced)

`changelog.html` is generated from `CHANGELOG.md` (mirror of the one in
`CannonFodder151/autobrain`) by `scripts/gen_changelog.py` — it rewrites only
the blocks between the `CHANGELOG-START` / `CHANGELOG-END` markers in
`changelog.html`. `[Unreleased]` is excluded from the public page.

- The deploy workflow regenerates it before every upload, so the site always
  matches the committed `CHANGELOG.md`.
- The autobrain repo's `dockerhub-publish.yml` syncs `CHANGELOG.md` here after
  every versioned deploy, so the site updates as part of the release flow
  (AUT-168 makes the changelog iteration mandatory in CI).
- **Only the 60 most recent releases are rendered.** `CHANGELOG.md` is a full
  append-only mirror (~146 KB / 149 releases) and rendering all of it produced a
  140 KB single page that crowded out crawl budget for every other page. Older
  releases link out to the full changelog in the `autobrain` repo. Override with
  `CHANGELOG_MAX_RELEASES=149 python3 scripts/gen_changelog.py`.

Regenerate locally: `python3 scripts/gen_changelog.py`

## Content

| Path | Purpose |
|------|---------|
| `index.html` | Marketing site: features, pricing, demo, self-host guide, contact |
| `features.html` | Full feature list with deterministic-first AI messaging |
| `hosted.html` | Plans & pricing (Free / Enthusiast / Garage) |
| `selfhost.html` | Self-host guide (MIT, simpler container stack) |
| `car-clubs.html` | Car clubs & community garage |
| `about.html` | About AutoBrain & Perfection IT Services |
| `contact.html` | Contact form + sales email |
| `car-diagnostics.html` | OBD2 diagnostics guide |
| `rego-status.html` | Rego Status (paid tier) explainer |
| `ownership-advisor.html` | Ownership Advisor (now live) |
| `petrol-price-map.html` | Petrol Price Map (WA + QLD live) |
| `obd2.html` | Custom OBD2 port (coming soon) |
| `ha-coming-soon.html` | Home Assistant Phase 2 (coming soon) |
| `coming-soon.html` | Electric Spy, EV Log Book, PHEV (Q4 2026) |
| `privacy.html` | Privacy policy |
| `ai-data.html` | AI & your data — what the AI reads per feature |
| `delete-account.html` | Account deletion |
| `changelog.html` | Public release changelog (auto-generated) |
| `blog.html` | Blog index |
| `blog/*.html` | 33 long-form SEO posts |
| `docs/positioning.md` | Positioning, pillars, content calendar (Phase 1 refresh) |
| `docs/petrol-price-map-launch-checklist.md` | Petrol Price Map launch readiness checklist |
| `docs/seo-review.md` | SEO audit & action items (refreshed 2026-09-28) |

The Android app is distributed through **Google Play closed testing** (no APK is
served from this site). The iOS app will be developed after Android reaches
general availability.

## Documentation

- **Repo docs:** `docs/` — positioning, launch checklists, feature docs.
- **Public wiki:** Outline collection "AutoBrain" at
  `https://outline.nathanmartina.com` (collection mirrors here where relevant).
- **Internal:** `AGENTS.md` (Graft wiring), `.github/workflows/` (CI/CD),
  `staticwebapp.config.json` (routing + security headers).

## Contact

sales@autobrainservice.app · [AutoBrain app source](https://github.com/CannonFodder151/autobrain)

<!-- AUT-1451 purge verification -->