# Blog Draft: Phase 1 — Simpler, Faster, More Reliable

**Issue:** AUT-3971
**Status:** Draft — pending human CMO approval
**Target channels:** autobrainservice.app/blog → Facebook → LinkedIn
**Publish date:** Immediately after approval

---

## Headline

**Phase 1 complete: AutoBrain is simpler, faster, and works even when AI is down**

## Meta description

Phase 1 rewrote AutoBrain's core around one principle: AI is an enhancement, not a dependency. Fewer containers, vectorised records, deterministic-first AI, and docs that stay in sync with the code. Your records stay usable even when the entire AI layer is offline.

## Body

### Lead

Phase 1 is live. We spent the last months rewriting AutoBrain's core around a single principle: **AI is an enhancement, not a dependency**. Every feature now runs a deterministic rule-based path first — 9Router only enriches the result when it's reachable and confident. Your maintenance history, diagnostics, valuations and receipts stay fully usable even when the AI layer is offline.

The stack is leaner, your data is vectorised and searchable, and the documentation has been rebuilt from the ground up. Here's what changed and why it matters.

---

### 1. Fewer containers, simpler operations

**What changed:** The hosted stack consolidated its long-running services. The standalone Celery worker now runs inside the backend image. The AI gateway was folded into the backend with shared utilities. No separate `minio-init` sidecar.

**Result:** 9 long-running containers → 8 (13 total services → 12). The same functionality, a smaller deployment surface to secure, monitor, and back up.

**Why it matters:** Self-hosted instances boot from a leaner container set. Fewer moving parts means fewer things to update, fewer network hops between services, and faster failover.

---

### 2. Your records are now vectorised and searchable

**What changed:** Service history, receipts, diagnostics, modifications and issues are embedded (1536-dim vectors via `text-embedding-3-small` on 9Router) and stored in your own PostgreSQL database with `pgvector`.

**Result:** Natural-language search over your garage — "show me all receipts mentioning timing belt" or "find diagnostics about P0420" — without an external index, without a third-party data pipeline, and entirely under your control. The `AI_ENABLED` toggle lets you disable embeddings entirely for cost control or offline deploys.

---

### 3. Deterministic-first AI: it works even when the router is down

**What changed:** Every AI feature now follows the `enhance()` pattern:

1. **Rule engine runs first.** A compiled Python module produces a deterministic baseline from real data — market anchors, manufacturer intervals, part-number tables, fault-code mappings.
2. **9Router is tried next.** If reachable, it gets the request. If unreachable, misconfigured, or it errors out, it returns `None` — no crash, no blank screen.
3. **Shallow-merge with guardrails.** If 9Router responds with confidence ≥ 0.75, its enrichment is merged — but deterministic-critical fields (`estimated_value`, `severity`, `service_type`, etc.) are **locked** and can never be overwritten.
4. **Transparent provenance.** Every response carries a `model` field: `rule-based+ai` when 9Router contributed, `rule-based-fallback` when it didn't.

**Real examples:**

- **Resale valuation:** 2010 Australian market anchors (Toyota Corolla $11k, Ford Falcon $14k, Nissan Patrol $24k) + depreciation curves provide the baseline. CarsGuide/CarSales medians override when cached. Valuation numbers are **immutable** — 9Router can add market commentary but never touches the estimate.
- **Diagnostics:** OBD codes (P0300 → misfire, P0420 → cat, P0171 → fuel trim lean) map to real part numbers (NGK BKR6EIX, DENSO 90919-02247) and a $120/hr labour rate. Structured guidance with confidence scores — no model needed.
- **Receipt OCR:** Australian vendor keyword matching (Supercheap, Repco, Autobarn) + item categories extracts totals, tax, line items — all regex, no model call.
- **Service prediction:** Manufacturer intervals (Toyota 20k km / 12 mo, timing belt 100k km / 60 mo) + measured history from your actual service gaps. BMWs get 10% more frequent intervals.

**The takeaway:** You can switch `AI_ENABLED=false` or self-host with no 9Router configured, and **diagnostics, valuations, receipt scanning and service prediction all keep working**. That's the difference between a feature and a gamble.

---

### 4. Modular code, easier to extend

**What changed:** The AI gateway is now a small set of shared utilities (`router_utils.py`) with per-module fallbacks in `fallbacks/`. Adding a feature means adding one module — not a new service to deploy, run, and maintain.

**Count:** 13 AI modules, 14 fallback implementations. Each module declares its immutable fields and allowed schema so a bad model response can never inject junk.

---

### 5. Documentation rebuilt from the ground up

**What changed:** The docs mirror (`docs/`) is now 8 structured sections — Company, Engineering, Deployment & Infrastructure, Security, Testing & QA, Marketing & Website, Finance, Business Reviews — each with an index, linked to the team wiki (Outline). The source-of-truth rule: when behaviour changes, update the matching Outline document and the repo mirror in the same change.

**New pages:** container-consolidation-migration.md, architecture.md, database-schema.md, api-spec.md, mobile-release.md, and a marketing section.

---

### What this means for you

| If you… | You get… |
|---------|----------|
| **Use the hosted app** | A more reliable service with fewer moving parts behind the scenes. Your AI features keep working during router outages. |
| **Self-host** | A leaner container stack that boots faster, uses less RAM, and still gives you full AI features if you configure 9Router — or deterministic fallbacks if you don't. |
| **Build on the API** | Predictable contracts: every AI response tells you `model: "rule-based+ai"` or `model: "rule-based-fallback"`. No silent failures. |
| **Care about privacy** | Vector search runs in your own database. The AI router only sees the minimal payload for the feature you trigger. You can run entirely offline. |

---

### Try it

The live demo at demo.autobrainservice.app (demo@autobrainservice.app / demo) runs the Phase 1 stack. Disable the AI router in your self-hosted instance — diagnostics, valuations and OCR still work.

---

### CTA

Read the technical deep-dive on the `enhance()` pattern and fallbacks → [AI & your data](/ai-data.html)  
Self-host the Phase 1 stack in 6 steps → [Self-Host](/selfhost.html)  
Watch the changelog → [Changelog](/changelog.html)

---

## Hashtags

#AutoBrain #Phase1 #CarMaintenance #AI #Determinism #Reliability #OpenSource #AustralianCars

---

## Technical source

Phase 1 work tracked in AUT-3461 (AI gateway consolidation), AUT-3153 (container consolidation), AUT-3813 (AI telemetry), and the Phase 1 improvement plan (`phase1-improvement-plan.md` in the repo). Key files: `ai/app/router_client.py` (`enhance()`), `ai/app/fallbacks/`, `backend/app/services/vector_search.py`, `docker-compose.hosted.yml`, `docs/Deployment-and-Infrastructure/container-consolidation-migration.md`.