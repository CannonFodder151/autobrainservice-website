# Petrol Price Map — Launch Readiness Checklist

Companion doc for the live page (`petrol-price-map.html`).
Viability research: AUT-1813. Implementation pipeline: AUT-1817.

## State coverage matrix (source of truth)

| State | Feed | Status | Notes |
|-------|------|--------|-------|
| WA | FuelWatch (`fuelwatch.wa.gov.au`) | Live | No API key required |
| QLD | Fuel Prices QLD (`fuelpricesqld.com.au`) | Live | Partner feed |
| NSW | FuelCheck (`data.nsw.gov.au`) | Launching soon | Partner-feed key pending |
| ACT | NSW FuelCheck feed | Launching soon | Partner-feed key pending (served from NSW) |
| VIC | Servo Saver (`service.vic.gov.au`) | Launching soon | Partner-feed key pending |
| SA | — | Coming soon | No free government feed (paid aggregators only) |
| TAS | — | Coming soon | No free government feed |
| NT | — | Coming soon | No free government feed |

## Flip-to-live checklist (run when the feature ships in the client)

- [x] Frontend feature ships behind the feature flag and is enabled in the client.
- [x] Verify each "Live" state returns current prices in the app (WA, QLD).
- [ ] NSW / ACT / VIC feed keys issued — move each pill from `status-next` to `status-live` as keys land.
- [ ] Any "Coming soon" state gains a free feed — move it to `Live`.
- [x] On `petrol-price-map.html`: the hero badge now reads **Now live** (not "Coming soon").
- [x] Hero/lead copy uses present-tense, live feature language.
- [x] "Want it sooner?" / `mailto:` CTA repointed to the live feature.
- [x] On `index.html`: Petrol Price Map Explore card shows **Now live** badge.
- [ ] Update CHANGELOG `[Unreleased]` — move the entry from "coming soon" to "shipped" (done in 0.3.282 per AUT-4289).
- [ ] Update this checklist: mark the feature live; archive when all states are Live or explicitly de-scoped.
- [x] Post a `#changelog` / `#updates` embed once live (done at launch).

## Site consistency

- `index.html` Explore card: `<div class="live u-badge-static">Now live</div>` ✅
- `petrol-price-map.html` hero: no "Coming soon" badge; title says "Live Fuel Prices for WA & QLD" ✅
- `coming-soon.html`: Petrol Price Map removed from coming-soon list ✅
- Nav menus: linked in More menu on all pages ✅

## Backlog

- NSW/ACT/VIC: partner-feed key acquisition tracked in AUT-1817 subtasks.
- SA/TAS/NT: evaluate paid aggregator partnerships (AUT-1813 follow-up).
- Servo Spy (price-watch alerts): tracked in AUT-1857, separate checklist.