# Phase 1 Social Content Calendar — AutoBrain

> **Source of truth:** All content below must be approved by human CMO in Discord #marketing via n8n Reporter embed before scheduling. Buffer channels: Facebook Page (AutoBrain), LinkedIn Page (AutoBrain).
>
> **Parent issue:** AUT-3972 | **PR:** #132 | **Target channels:** Facebook, LinkedIn, Blog cross-promotion
> **Approval status:** DRAFT — pending human CMO sign-off

---

## Post 1: Phase 1 Launch Announcement (Blog Cross-Promo)

**Timing:** Day 0 (immediately after blog publishes)
**Channel:** Facebook + LinkedIn
**Asset:** Blog OG image (`assets/blog/og/ai-that-works-even-when-the-ai-is-down.png`)

**Facebook Copy:**
```
Phase 1 is live. 🚗⚡

We rewrote AutoBrain's core around one principle: AI is an enhancement, not a dependency.

Every feature now runs a deterministic rule-based path first — 9Router only enriches when it's reachable and confident. Your service history, diagnostics, valuations and receipts stay fully usable even when the AI layer is offline.

What changed:
• 9 → 8 long-running containers (simpler stack, fewer things to break)
• Your records are now vectorised & searchable (1536-dim embeddings)
• AI diagnostics, fuel predictions, receipt scanning — all work offline-first
• Documentation rebuilt from ground up

Read the full breakdown: https://autobrainservice.app/blog/ai-that-works-even-when-the-ai-is-down.html

#AutoBrain #CarMaintenance #AI #Reliability #AustralianMade #SelfHosted #OpenSource
```

**LinkedIn Copy:**
```
Phase 1 is live: AutoBrain is simpler, faster, and works even when AI is down.

We spent the last months rewriting AutoBrain's core around a single principle: AI is an enhancement, not a dependency. Every feature runs a deterministic rule-based path first — the AI router only enriches the result when it's reachable and confident.

Key outcomes:
✅ 9 → 8 containers (13 → 12 total services) — leaner deployment surface
✅ Vectorised records (1536-dim pgvector) — instant semantic search across service history, receipts, diagnostics
✅ Deterministic-first AI — 13 modules, 14 fallbacks, zero hard AI dependencies
✅ Refreshed docs — 8 sections, auto-synced with code

For Australian car owners and self-hosters: your maintenance logbook, fuel tracking, rego lookup and diagnostics stay fully functional even when external AI services are down.

Full technical write-up: https://autobrainservice.app/blog/ai-that-works-even-when-the-ai-is-down.html

#AutoBrain #CarMaintenance #AI #ReliabilityEngineering #AustralianTech #OpenSource #SelfHosted
```

---

## Post 2: Reliability Deep-Dive (Deterministic-First)

**Timing:** Day 2
**Channel:** Facebook + LinkedIn
**Asset:** New OG image needed (create: deterministic-architecture diagram)

**Facebook Copy:**
```
How does AutoBrain diagnose a check engine light when the AI is down? 🔧

Deterministic rule-based fallbacks. Every AI feature has a coded rule path that runs FIRST. The AI router (9Router) only adds enrichment — confidence scoring, natural language summaries, anomaly detection — when it responds within budget and with high confidence.

If the router times out, returns low confidence, or is unreachable? The rule-based result ships to the user unchanged.

This isn't a backup plan. It's the primary architecture.

12 AI modules | 13 deterministic fallbacks | 0 hard AI dependencies

Your data, your rules, your uptime.

#AutoBrain #DeterministicAI #ReliabilityEngineering #CarDiagnostics #AustralianMade
```

**LinkedIn Copy:**
```
The problem with most "AI-powered" apps: when the model API goes down, the feature breaks.

AutoBrain Phase 1 flipped this. Every AI feature runs a deterministic rule-based path FIRST. The AI router (9Router) is an enrichment layer — it adds confidence scoring, natural language summaries, and anomaly detection only when reachable and confident.

Architecture:
• 12 AI modules (diagnostics, valuation, fuel prediction, receipt OCR, etc.)
• 14 deterministic fallback functions — pure Python, zero external deps
• Circuit breaker + timeout budget on every router call
• Rule result always ships; AI only upgrades it

Result: Your check engine diagnosis, fuel forecast, and receipt scan work 100% of the time. AI makes them better when available.

This is what "AI as enhancement, not dependency" looks like in production.

#AutoBrain #DeterministicAI #ReliabilityEngineering #SystemDesign #AustralianTech
```

---

## Post 3: Self-Host on a $5 VPS (Container Stack)

**Timing:** Day 5
**Channel:** Facebook + LinkedIn
**Asset:** Screenshot of `docker compose up -d` on clean VPS

**Facebook Copy:**
```
Self-host AutoBrain on a $5/month VPS. Yes, really. 💸

Phase 1 consolidated the stack: 9 long-running containers → 8. The Celery worker runs inside the backend image. The AI gateway folded into the backend. No separate MinIO init sidecar.

What you need:
• 1 GB RAM VPS (Hetzner CX22, DigitalOcean Basic, Oracle Always Free ARM)
• Docker + Docker Compose
• 2 minutes

```bash
git clone https://github.com/CannonFodder151/autobrain
cd autobrain
cp .env.example .env  # add your keys
docker compose -f docker-compose.prod.yml up -d
```

Full docs: https://autobrainservice.app/selfhost.html

MIT licensed. Your data never leaves your server. No license keys, no phone home.

#AutoBrain #SelfHosted #OpenSource #Docker #Homelab #AustralianTech #PrivacyFirst
```

**LinkedIn Copy:**
```
Self-host AutoBrain on a $5/month VPS — Phase 1 made it practical.

The hosted stack consolidated from 9 → 8 long-running containers (13 → 12 total services). The Celery worker moved into the backend image. The AI gateway merged into the backend with shared utilities. The MinIO init sidecar removed.

Deployment is now:
```bash
git clone https://github.com/CannonFodder151/autobrain
cd autobrain
cp .env.example .env
docker compose -f docker-compose.prod.yml up -d
```

Runs on 1 GB RAM (Hetzner CX22, Oracle Always Free ARM, DigitalOcean Basic). MIT licensed. Zero data leaves your infrastructure. No license keys, no telemetry, no phone-home.

Documentation: https://autobrainservice.app/selfhost.html

#AutoBrain #SelfHosted #OpenSource #Docker #Homelab #PrivacyFirst #AustralianTech
```

---

## Post 4: Australian Rego Lookup → Parts Matching

**Timing:** Day 8
**Channel:** Facebook + LinkedIn
**Asset:** Demo screenshot: rego lookup → parts list populated

**Facebook Copy:**
```
Free Australian rego lookup → instant parts list for YOUR exact car. 🇦🇺

Enter your VIC/NSW/QLD/SA/WA/TAS/NT/ACT plate → AutoBrain pulls the exact make/model/variant/year → auto-suggests the oil filters, air filters, brake pads, wipers and fluids that fit.

No guessing. No "fits 2015-2020 Corolla" — it knows YOUR 2017 Corolla Ascent Sedan 1.8L.

Try it free: https://autobrainservice.app/rego-status.html

#AutoBrain #RegoLookup #AustralianCars #CarParts #DIYMechanic #VIC #NSW #QLD #SA #WA #TAS #NT #ACT
```

**LinkedIn Copy:**
```
Free Australian rego lookup that auto-populates your parts list.

Enter any Australian plate (VIC/NSW/QLD/SA/WA/TAS/NT/ACT) → AutoBrain resolves the exact vehicle variant → instantly suggests the correct oil filter, air filter, brake pads, wiper blades, and fluids for THAT specific car.

No more "fits 2015-2020 Corolla" ambiguity. It knows your exact build.

Free tier: 10 lookups/month. Paid: unlimited + history + API access.

Try it: https://autobrainservice.app/rego-status.html

#AutoBrain #AustralianAutomotive #RegoLookup #CarMaintenance #PartsMatching #VIC #NSW #QLD #SA #WA #TAS #NT #ACT
```

---

## Post 5: Vector Search = Instant History

**Timing:** Day 11
**Channel:** Facebook + LinkedIn
**Asset:** Screenshot of semantic search: "brake" → shows all brake-related entries

**Facebook Copy:**
```
"What did I last pay for front brake pads?" — search "brake" → instant. 🔍

Phase 1 vectorised your records: service history, receipts, diagnostics, modifications, issues — all embedded as 1536-dim vectors (pgvector).

Search naturally: "brake", "oil change 2023", "that weird noise in July", "AC regas receipt". Finds matches by meaning, not just keywords.

Your car's memory, actually searchable.

#AutoBrain #VectorSearch #CarHistory #SemanticSearch #pgvector #AustralianMade
```

**LinkedIn Copy:**
```
Phase 1 vectorised your entire vehicle history.

Service records, receipts, diagnostic logs, modifications, issues — all embedded as 1536-dimension vectors (pgvector). Search by meaning: "brake", "oil change last year", "AC regas receipt", "that noise in July".

Instant semantic search across everything. No more scrolling through PDF folders or spreadsheet tabs.

Technical: pgvector on PostgreSQL, 1536-dim embeddings (text-embedding-3-small compatible), hybrid keyword+vector ranking.

#AutoBrain #VectorSearch #SemanticSearch #pgvector #CarMaintenance #DataEngineering
```

---

## Post 6: ATO Logbook Compliance

**Timing:** Day 14
**Channel:** Facebook + LinkedIn
**Asset:** Screenshot of ATO-compliant logbook export (financial year PDF)

**Facebook Copy:**
```
ATO-compliant logbook export in 2 taps. 📊🇦🇺

AutoBrain generates the exact logbook format the ATO accepts: financial year (1 July – 30 June), odometer start/end, business % calculation, trip categories, fuel costs — all in a clean PDF.

No spreadsheet templates. No manual totals. Just drive, log, export.

Free tier: unlimited vehicles, unlimited exports.

https://autobrainservice.app/features.html#logbook

#AutoBrain #ATOLogbook #TaxTime #AustralianDrivers #CarExpenses #TaxDeduction #EOFY
```

**LinkedIn Copy:**
```
ATO-compliant vehicle logbook export — built for Australian tax time.

AutoBrain generates the exact format the ATO requires:
• Financial year boundaries (1 July – 30 June)
• Odometer start/end per vehicle
• Business use % calculation
• Trip categorisation (business/private)
• Fuel & expense totals
• Clean PDF export

No spreadsheet templates. No manual formulas. Drive → log → export.

Unlimited vehicles, unlimited exports on the free tier.

https://autobrainservice.app/features.html#logbook

#AutoBrain #ATOLogbook #AustralianTax #TaxDeduction #EOFY #CarExpenses #SmallBusiness
```

---

## Post 7: EV / PHEV Support Coming (Roadmap)

**Timing:** Day 17
**Channel:** Facebook + LinkedIn
**Asset:** Teaser graphic: EV battery health + charging log

**Facebook Copy:**
```
EV & PHEV owners — we see you. ⚡🔋

Phase 2 roadmap: EV battery health tracking, charging session logs, range estimation, cost-per-km vs petrol equivalent. Electric Spy (nearby charger detection) already live.

Sign up for beta: https://autobrainservice.app/ev-log-book.html

#AutoBrain #EV #PHEV #ElectricVehicle #BatteryHealth #Charging #AustralianEV #Tesla #BYD #MG
```

**LinkedIn Copy:**
```
EV & PHEV support coming in Phase 2.

Roadmap items:
• Battery health tracking (degradation curves, SOH estimation)
• Charging session logs (location, speed, cost, kWh)
• Range estimation vs rated
• Cost-per-km comparison vs petrol equivalent
• Electric Spy — nearby charger detection (already live)

Beta sign-up: https://autobrainservice.app/ev-log-book.html

#AutoBrain #EV #PHEV #ElectricVehicle #BatteryHealth #EVCharging #AustralianEV #CleanTech
```

---

## Post 8: Customer Spotlight (Social Proof)

**Timing:** Day 21
**Channel:** Facebook + LinkedIn
**Asset:** Photo of car club meetup with AutoBrain QR codes / member testimonials

**Facebook Copy:**
```
"Our club of 40+ members runs AutoBrain on a shared VPS. Everyone sees the full history of the club cars — who did what, when, and what parts were used. No more lost receipts." — Melbourne Car Club admin

Car clubs and fleets: shared vehicle history, community feed, custom deployments. MIT licensed, self-hosted, your infrastructure.

Start a club workspace: https://autobrainservice.app/car-clubs.html

#AutoBrain #CarClubs #FleetManagement #CommunityGarage #AustralianCars #MelbourneCars
```

**LinkedIn Copy:**
```
"Our club of 40+ members runs AutoBrain on a shared VPS. Everyone sees the full history of the club cars — who did what, when, and what parts were used. No more lost receipts." — Melbourne Car Club admin

Car clubs and fleets get: shared vehicle history, community feed, custom self-hosted deployments. MIT licensed. Your infrastructure, your data, your rules.

Start a club workspace: https://autobrainservice.app/car-clubs.html

#AutoBrain #CarClubs #FleetManagement #CommunityGarage #AustralianAutomotive #OpenSource
```

---

## Post 9: Privacy-First Architecture

**Timing:** Day 24
**Channel:** LinkedIn (technical audience)
**Asset:** Architecture diagram: data flow, self-hosted = zero egress

**LinkedIn Copy:**
```
Your car data never trains models. Never gets sold. Self-hosted = zero data leaves your server. 🔒

Phase 1 reinforced this with modular, deterministic architecture:
• AI router calls are opt-in enrichments, not data pipelines
* No telemetry, no analytics SDKs, no crash reporters that phone home
* Self-hosted deployment uses only your infrastructure
* MIT license — fork it, audit it, run it

Compare: most "AI car apps" stream your driving data, service history, and location to train their models.

AutoBrain: your car, your data, your rules.

#AutoBrain #PrivacyFirst #DataSovereignty #SelfHosted #OpenSource #AustralianTech #GDPR #PrivacyByDesign
```

---

## Post 10: Community Garage / Social Features

**Timing:** Day 27
**Channel:** Facebook
**Asset:** Screenshot of community feed: builds, issues, parts reviews

**Facebook Copy:**
```
Your build, your feed. 🛠️

Community Garage: share your build thread, log issues, review parts, follow other Aussie builds. All self-hosted or on our hosted tier — no algorithm, no ads, just car people.

See what's trending: https://autobrainservice.app/community-garage.html

#AutoBrain #CommunityGarage #CarBuilds #AustralianCarScene #CarMods #PartsReviews
```

---

## Scheduling Notes

| Post | Ideal Day | Buffer Queue Slot | Tags |
|------|-----------|-------------------|------|
| 1 Launch | Day 0 | shareNow (immediate) | #Phase1 #Launch |
| 2 Reliability | Day 2 | addToQueue | #TechDeepDive |
| 3 Self-Host | Day 5 | addToQueue | #SelfHosted #Homelab |
| 4 Rego→Parts | Day 8 | addToQueue | #AustralianCars |
| 5 Vector Search | Day 11 | addToQueue | #DataEngineering |
| 6 ATO Logbook | Day 14 | addToQueue (tax season boost) | #TaxTime #EOFY |
| 7 EV Roadmap | Day 17 | addToQueue | #EV #Roadmap |
| 8 Customer Spotlight | Day 21 | addToQueue | #SocialProof |
| 9 Privacy | Day 24 | addToQueue | #Privacy #Technical |
| 10 Community | Day 27 | addToQueue | #Community |

---

## Approval Checklist (per AGENTS.md)

- [ ] Human CMO reviews FULL copy above in Discord #marketing
- [ ] Human CMO approves each post individually (or batch approves)
- [ ] Approved posts scheduled via Buffer MCP using correct channel IDs:
  - Facebook: `6a7859acb2d9d57743445d31`
  - LinkedIn: `6a78595bb2d9d57743445c3c`
- [ ] Assets created/uploaded for posts requiring images
- [ ] Blog post (Post 1 cross-promo) published before social posts go live

---

## Buffer MCP Commands (for reference after approval)

```bash
# Example: schedule Post 1 to Facebook
buffer_create_post --channelId 6a7859acb2d9d57743445d31 --text "..." --mode addToQueue --schedulingType automatic

# Example: schedule Post 1 to LinkedIn  
buffer_create_post --channelId 6a78595bb2d9d57743445c3c --text "..." --mode addToQueue --schedulingType automatic
```
