# AutoBrain Positioning & Content Calendar (Phase 1 Refresh)

> Aligned with Phase 1 code-review outcomes: deterministic-first AI, simpler container stack, vectorised data, modular architecture, refreshed docs.

## Core positioning

**Tagline:** *Australian car maintenance with reliable AI.*

**Elevator pitch:** AutoBrain is the car maintenance tracker built for Australicians — digital logbook, rego lookup, fuel tracking, AI diagnostics and resale estimates. A rego lookup also auto-suggests the parts that fit the exact vehicle, so the parts list and inventory start populated instead of blank. The AI works even when external AI services are unreachable (deterministic rule-based fallbacks first), and you can self-host it for free or let us run it for you.

## Pillars

| Pillar | Messaging | Phase 1 driver |
|--------|-----------|----------------|
| **Reliable AI** | AI features route through deterministic rule-based paths first; AI is the enhancement, not the dependency. | Deterministic-first AI with fallbacks (code review c) |
| **Australian-built** | ATO logbook, L/100km, rego lookup, AU financial-year exports. Built for Australian cars and regulations. | N/A (market focus) |
| **Self-host or hosted** | MIT-licensed open source → run on your own $5 VPS or use our hosted tier. No lock-in. | Simpler container stack (code review a) |
| **Privacy-first** | Your data never trains models or gets sold. Self-hosted = zero data leaves your server. | Modular, deterministic architecture (code review b, d) |

## Audience tiers

1. **DIY enthusiasts** — wrench in the garage, track mods, want local data control.
2. **Daily drivers** — ATO logbook, fuel costs, service reminders.
3. **Car clubs / fleets** — shared vehicle history, community feed, custom deployments.

## Content calendar (4-week outline)

| Week | Topic | Channel | Goal |
|------|-------|---------|------|
| Week 1 | "Why AutoBrain keeps working when AI is down" (deterministic-first) | Blog → #blog, Facebook | Educate on reliability |
| Week 2 | "Self-host AutoBrain on a $5/month VPS" (simpler stack) | Blog → #blog, GitHub | Drive self-hosting |
| Week 3 | "ATO logbook made simple for Australian drivers" | Blog → #blog, Facebook | Drive ATO compliance sign-ups |
| Week 4 | Customer spotlight: car club using AutoBrain | #updates, Facebook | Social proof |

## Scheduled week: Mon 28 Sep – Sun 4 Oct 2026 (AUT-4422 batch)

Cadence restored to 2 posts/day across LinkedIn + Facebook, with two blog publishes. All items require
human CMO approval in Discord #marketing before scheduling (see Approval gate below).

| Date | Channel | Item | Type |
|------|---------|------|------|
| Mon 28 Sep | LinkedIn | AutoBrain batch kickoff — reliable AI + AU-built positioning | Social post |
| Mon 28 Sep | Facebook | Community question: what breaks first on your car? | Social post |
| Wed 30 Sep | LinkedIn | Promo: "Fair Price for Used Cars 2026" blog | Social post |
| Wed 30 Sep | Facebook | Share: "Fair Price for Used Cars 2026" blog | Social post |
| Fri 2 Oct | LinkedIn | Promo: "OBD2 Adapter Buying Guide 2026" blog | Social post |
| Fri 2 Oct | Facebook | Share: "OBD2 Adapter Buying Guide 2026" blog | Social post |
| Sun 4 Oct | LinkedIn | Ownership Advisor case study carousel | Social carousel |
| Sun 4 Oct | Facebook | Community story: Ownership Advisor case study | Social post |
| Wed 1 Oct | Blog | Publish "Fair Price for Used Cars 2026" | Blog publish |
| Fri 3 Oct | Blog | Publish "OBD2 Adapter Buying Guide 2026" | Blog publish |

> This table is the repo mirror of the Outline content calendar. Outline sync is tracked in AUT-4520.
> Note (AUT-5737 W40 review): the W40 plan above was NOT executed. Buffer shows 0 posts scheduled and 0 posts
> sent for the Mon 28 Sep – Sun 4 Oct window. No content hit either channel. Root cause to be confirmed with
> the human CMO; the W40 slot is recorded as `missed` and rolled into the W41 recovery plan below.

## Weekly review: W40 (Mon 28 Sep – Sun 4 Oct 2026) — AUT-5737

Routine: `4c26d2eb-...` (Weekly content & engagement review, Mon 10:00 UTC). Run by CMO (agent `e90b3043`).

### Sources
- **Buffer** — org `6a78592a2d73d2fb75467892`; channels FB `6a7859acb2d9d57743445d31`, LI `6a78595bb2d9d57743445c3c`.
- **Outline** — Social Content Calendar `9d1b2716-…`, Content Calendar (blog) `ca2d5b64-…`. *Not written back this run: the `outline_api_token` secret is not granted to the CMO agent. Repo mirror updated instead; AUT-4520 sync pending a secret grant.*
- **Blog** — `CannonFodder151/autobrainservice-website` repo; `blog/*.html` published, `drafts/*.md` pending approval.

### Findings

1. **Cadence was broken.** Zero posts scheduled and zero sent across both channels for the
   entire Mon 28 Sep – Sun 4 Oct week. Buffer queue is empty. The W40 calendar block
   (10 items: 4 social + 2 blog + 4 promo) did not ship.
2. **Trailing volume (real posts, excluding Aug 6–12 smoke tests).** Sep 5 – Oct 4:
   - **LinkedIn:** 8 posts — 112 impressions, 0 reactions, 0 comments, 0 shares.
     Top: "Ownership Advisor is now live" (Sep 25) → 12 impressions, 0% ER.
   - **Facebook:** 8 posts — 65 impressions, 0 reactions, 0 comments, 0 shares.
     Top: "Smart Vehicle Logbook" (Aug 6) → 520 impressions, 11.54% ER, 2 shares;
     "Android app cleared the bar" (Aug 21) → 101 impressions.
3. **Engagement is low and declining** inside the window. No post in Sep 5–Oct 4 crossed
   the playbook's "healthy" bar (ER ≥ 5%, clicks ≥ 10, shares ≥ 1). ER is 0.0–2.2% across
   the period; the only shares in the window were on the older Aug logbook post.
4. **Top performer pattern:** the Aug 6 Facebook logbook post — product education with a
   clear value proposition and emoji hook — is the single best-performing asset in the
   last 60 days. Long-form LinkedIn explainers sit at ~12 impressions with 0 engagement.
5. **Blog drafts ready for approval (awaiting human CMO sign-off in #marketing):**
   - `drafts/AUT-1718-ai-deterministic-draft.md` — "AI that works even when the AI is down"
     (matches W1 calendar topic "Why AutoBrain keeps working when AI is down").
   - `drafts/AUT-2540-HA-coming-soon.md` — Home Assistant integration landing (cluster C;
     status unconfirmed → do NOT publish until product confirms HA shipped).
   - `drafts/AUT-1490-obd2-adapter-blog.md` — OBD2 adapter deep-dive.

### Next-week suggestions: W41 recovery plan (Mon 4 Oct – Sun 10 Oct)

**Blog** (2 posts, Tue + Thu cadence):
- Tue 7 Oct — publish "Fair Price for Used Cars 2026" (W40 carryover, already drafted on
  `blog/fair-price-used-car-2026.html`, needs approval).
- Thu 9 Oct — publish "OBD2 Adapter Buying Guide 2026" (W40 carryover, already drafted on
  `blog/obd2-adapter-buying-guide-2026.html`, needs approval).
- *Hold* AUT-1718 "AI that works even when the AI is down" for W42 W1 topic until W41 cadence
  is proven back. (SEO brief §5 / cluster C defers HA page.)

**Social (3–5 posts, LI 2 + FB 2):**
- Mon 5 Oct (today, catch-up) — LI: "Fair Price for Used Cars 2026" blog promo (hook: "Is your
  trade-in being short-changed?").
- Mon 5 Oct — FB: community question "What's the one repair you always forget to log?" (engagement).
- Wed 7 Oct — LI: "OBD2 Adapter Buying Guide 2026" promo (hook: "OBD2 is not magic — here's how to read what it actually says").
- Wed 7 Oct — FB: share the OBD2 guide (hook: same).
- Sun 10 Oct — LI + FB: Ownership Advisor mini-case (repurpose Sep 25 asset; the "live" post underperformed — add the numbers hook).

**Content / evergreen:**
- Refresh: the Sep 25 "Ownership Advisor is live" LinkedIn post earned 12 impressions and 0
  engagement — the hook (product-announce copy) is weak. Next Ownership Advisor promo leads
  with a number ("X% of users get a valuation in <Y sec").

### Acceptance checklist
- [x] Buffer metrics pulled (sent, last 7 + last 30, exclude smoke tests)
- [x] Blog drafts inventoried + statuses noted
- [x] W40 miss diagnosed; W41 recovery plan written
- [x] Repo mirror `docs/positioning.md` updated (W40 review + W41 plan)
- [ ] Outline Social Content Calendar updated (BLOCKED on `outline_api_token` grant — see AUT-5107/5401)
- [ ] Discord #updates status posted

> This review was produced by the CMO agent (AUT-5737). Nothing above was published to any
> public channel — it is a report. All publishing remains gated on human CMO approval in
> Discord #marketing.

## Channels

- **Website** (autobrainservice.app) — primary marketing surface
- **Blog** — long-form SEO + feature education
- **Facebook** — community engagement
- **Discord #support / #changelog** — customer-facing updates
- **Discord #updates** — internal change reports

## Approval gate

All content is drafted and reviewed in Discord #marketing by the human CMO before publishing. No auto-posting.
