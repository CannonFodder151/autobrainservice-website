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
