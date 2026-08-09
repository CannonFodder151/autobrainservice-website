# AutoBrain Website

Public marketing site for **AutoBrain** — the AI-powered car companion.

**Live:** https://autobrainservice.app
**Demo app:** https://demo.autobrainservice.app

## Hosting

Deployed as an **Azure Static Web App** (free tier) from this private repo. DNS for `autobrainservice.app` points at the SWA endpoint (see the Azure portal; currently proxied via Cloudflare).

- App location: `/` (static site, no build step — `skip_app_build: true`)
- Config: [`staticwebapp.config.json`](staticwebapp.config.json) (routing, headers, `.apk` MIME type)
- Deploy workflow: Azure Static Web Apps publish action in [`.github/workflows/`](.github/workflows/)
- Requires the Azure SWA deployment-token secret configured in GitHub (set via the Azure portal, "Manage deployment token")

## Changelog (auto-synced)

`changelog.html` is generated from `CHANGELOG.md` (mirror of the one in
`CannonFodder151/autobrain`) by `scripts/gen_changelog.py` — it rewrites only
the blocks between the `CHANGELOG-START` / `CHANGELOG-END` markers in
`changelog.html`. `[Unreleased]` is excluded from the public page.

- The deploy workflow regenerates it before every upload, so the site always
  matches the committed `CHANGELOG.md`.
- The autobrain repo's `build-hosted.yml` syncs `CHANGELOG.md` here after every
  versioned deploy, so the site updates as part of the release flow.

Regenerate locally: `python3 scripts/gen_changelog.py`

## Content

| Path | Purpose |
|------|---------|
| `index.html` | Marketing site: features, pricing, demo, self-host guide, contact |
| `logo.png` | AutoBrain logo |
| `assets/logo.png` | Logo (icon) |
| `downloads/autobrain.apk` | Android APK served for the in-app "Get the app" button |

Update the Android app from `CannonFodder151/autobrain` (frontend) and drop the built
`build/app/outputs/flutter-apk/app-release.apk` here as `downloads/autobrain.apk`.

## Contact

sales@autobrainservice.app · [AutoBrain app source](https://github.com/CannonFodder151/autobrain)
