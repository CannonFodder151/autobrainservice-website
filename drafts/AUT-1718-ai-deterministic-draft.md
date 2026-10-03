# Blog Draft: AI that works even when the AI is down

**Issue:** AUT-1718
**Status:** Draft — pending human CMO approval
**Target channels:** autobrainservice.app/blog → Facebook
**Publish date:** Immediately after approval

---

## Headline

**AI that works even when the AI is down**

## Meta description

AutoBrain treats AI as an enhancement, not a dependency. Every AI feature routes through a deterministic rule-based path first — 9Router AI enriches the result only when reachable. Your records stay usable even when the router is down.

## Body

### Lead

AutoBrain treats AI as an enhancement, not a dependency. Every AI feature routes through a deterministic rule-based path first — 9Router only enriches the result when it can reach the model. Your records stay usable even when the entire AI layer is down. That's the difference between a feature and a gamble.

### The problem with AI-first everything

A lot of "AI-powered" tools quietly break when the model call fails. You tap a button, nothing happens, and the whole screen feels dead — even though the data underneath was always yours. When a maintenance log is involved, that's not just annoying; it's the moment you lose trust in the tool.

### Deterministic first, AI as a layer on top

AutoBrain was rebuilt in Phase 1 around the opposite idea: the core operations are deterministic, rule-based paths that **always** work — calculations, scheduling, exports, reminders. AI is added on top where it genuinely helps, and every AI feature keeps a fallback:

- **Predictive maintenance** still runs on schedule-based rules if the model isn't reachable.
- **Rego lookup** is a direct, reliable data lookup — not an AI guess.
- **Diagnostics** give you structured guidance from fault codes even without a model response.
- **Self-hosted instances** can run entirely on rule-based paths, with nothing leaving your server.

### How it works: the `enhance()` pattern

Every AI feature in AutoBrain follows the same architecture. Here's the flow:

1. **Rule engine runs first.** A compiled Python module produces a deterministic baseline result from tables of real data — part numbers, market prices, service intervals, fault codes.
2. **9Router AI is tried next.** The request goes to 9Router at `AI_ROUTER_URL`. If the router is unreachable, misconfigured, or returns an error, it returns `None` — no crash, no blank screen.
3. **Shallow-merge with guardrails.** If 9Router responds, its enrichment is merged into the baseline — but deterministic-critical fields are locked down and can never be overwritten. A bad model guess can't touch the numbers.
4. **Transparent provenance.** Every response carries a `model` field: `rule-based-fallback` when the router was down, or `rule-based+ai` when it contributed.

If the network drops, the firewall blocks the call, or 9Router has an outage — you get the rule-based result, uninterrupted.

### Real examples from the code

#### Resale valuation: market anchors + depreciation curves

When you ask "what's my car worth?", a static table of 2010 Australian market anchors (Toyota Corolla: $11,000, Ford Falcon: $14,000, Nissan Patrol: $24,000) provides the base. A depreciation curve (100% residual at age 0, 41% at age 10, 18% floor) adjusts for vehicle age. Real CarsGuide/CarSales listing medians — cached, not re-fetched every call — override the estimate when available.

The numbers (`estimated_value`, `low`, `high`) are marked **immutable** in the gateway — 9Router can add market facts and advice, but it can never touch the valuation itself. A bad model guess can't skew your quote.

#### Diagnostics: OBD codes + part number lookups

Your check-engine light? The rule engine matches your OBD code (P030 → misfire, P042 → catalytic converter, P0171 → fuel trim lean) against a compiled table of fault patterns, each with real part numbers (NGK BKR6EIX spark plugs, DENSO 90919-02247 ignition coils) and a $120/hr labour rate. You get structured guidance with confidence scores and part recommendations — no model needed.

#### Receipt OCR: Australian vendor keyword matching

Snap a service invoice and the rule engine uses keyword matching against Australian vendors (Supercheap, Repco, Autobarn) and item categories (oil → $80, brake pads → $120, MAF sensor → $150) to extract totals, tax, and line items — all with regex, no model call.

#### Service prediction: manufacturer intervals + measured history

The rule engine knows a Toyota scheduled service is 20,000 km / 12 months, a timing belt is 100,000 km / 60 months, and that BMWs need service 10% more frequently. If you've logged previous services, it measures the actual gap between them and uses that real interval for the next prediction.

### The `model` field: transparency you can trust

Every AI response includes a `model` field. When 9Router contributed enrichment it reads `rule-based+ai`. When it fell back to pure rules it reads `rule-based-fallback`. No spin, no ambiguity — you always know whether you're seeing the deterministic baseline or the AI-enhanced version.

### Reliability is a privacy feature too

If the AI layer can be switched off and the app still works, then a privacy-conscious self-hoster isn't forced to send their vehicle data anywhere. You get the choice. That's the design we wanted: **AI that's a tool you control, not a service you depend on.**

### CTA

Fire up the live demo — valuations, diagnostics, and OCR stay fully functional with the model layer disabled. Or self-host AutoBrain on a $5/month VPS in five minutes, running entirely on rule-based paths with nothing leaving your server.

## Hashtags

#AutoBrain #CarMaintenance #AI #Determinism #Reliability #AustralianCars #OpenSource

## Technical source

Draft based on code review of `ai/app/router_client.py` (`enhance()` function), `ai/app/modules/resale.py`, `ai/app/fallbacks/resale.py`, `ai/app/fallbacks/diagnose.py`, `ai/app/fallbacks/ocr.py`, `ai/app/fallbacks/service_prediction.py`.
