# Petrol Price Map — Launch Readiness Checklist

Companion doc for the coming-soon landing page (`petrol-price-map.html`, AUT-1857).
Viability research: AUT-1813. Implementation pipeline: AUT-1817.

## State coverage matrix (source of truth)

| State | Feed | Status | Notes |
|-------|------|--------|-------|
| WA  | FuelWatch (`fuelwatch.wa.gov.au`) | Live | No API key required |
| QLD | Fuel Prices QLD (`fuelpricesqld.com.au`) | Live | Partner feed |
| NSW | FuelCheck (`data.nsw.gov.au`) | Launching soon | Partner-feed key pending |
| ACT | NSW FuelCheck feed | Launching soon | Partner-feed key pending (served from NSW) |
| VIC | Servo Saver (`service.vic.gov.au`) | Launching soon | Partner-feed key pending |
| SA  | — | Coming soon | No free government feed (paid aggregators only) |
| TAS | — | Coming soon | No free government feed |
| NT  | — | Coming soon | No free government feed |

## Flip-to-live checklist (run when the feature ships in the client)

- [ ] Frontend feature ships behind the feature flag and is enabled in the client.
- [ ] Verify each "Live" state returns current prices in the app (WA, QLD).
- [ ] NSW / ACT / VIC feed keys issued — move each pill from `status-next` to `status-live` as keys land.
- [ ] Any "Coming soon" state gains a free feed — move it to `Live`.
- [ ] On `petrol-price-map.html`: remove the `<div class="soon u-badge-static-center">Coming soon</div>` hero badge.
- [ ] Rewrite the hero/lead copy from "coming soon" framing to present-tense, live feature language.
- [ ] Remove the "Want it sooner?" / `mailto:` CTA (or repoint it to the live feature).
- [ ] On `index.html`: remove the `Coming soon` badge from the Petrol Price Map Explore card.
- [ ] Update CHANGELOG `[Unreleased]` — move the entry from "coming soon" to "shipped".
- [ ] Update this checklist: mark the feature live; archive when all states are Live or explicitly de-scoped.
- [ ] Post a `#changelog` / `#updates` embed once live.
