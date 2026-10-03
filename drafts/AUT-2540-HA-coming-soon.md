# AUT-2540 — Home Assistant Integration Coming Soon Page Draft

> Updated 2026-09-09 for AUT-3156: page content corrected from "High-Availability migration" to "Home Assistant integration coming soon".
> The `ha-` in the URL stands for **Home Assistant**, not High Availability.
> The HA migration page content was moved to a separate internal issue (AUT-2540-HA-migration) — this page is the dedicated Home Assistant integration announcement.

## Page: `/ha-coming-soon.html`

### Hero

**Headline:** AutoBrain is coming to Home Assistant

**Subhead:** Your car already lives in your phone — but it deserves better than a standalone app. AutoBrain is joining Home Assistant, pushing service reminders, fuel analytics, and running costs onto the same dashboard as your lights, locks, and laundry. Phase 1 lands in Q4 2026, with a closed beta opening in October.

**CTA:** Join the HA waitlist → (mailto:sales@autobrainservice.app?subject=HA%20waitlist)

### What's coming

- **Service reminder sensors** — countdown entities per vehicle showing kilometres and days until the next service. Drop them into a Lovelace card or an HA todo list.
- **Fuel economy trends** — rolling L/100km averages sitting next to your solar production on the same dashboard.
- **Cost analytics** — total spend by category (fuel, service, rego), month-on-month deltas, and cost per kilometre rendered in native HA charts.

### How the integration works

AutoBrain acts as the intelligence layer. It computes your analytics and service intervals, then pushes only the processed insights into Home Assistant — no raw telemetry, no cloud dependency, nothing leaving your network unless you want it to.

- **Phase 1 (Q4 2026):** REST + WebSocket feed. Pull AutoBrain analytics and service-interval pushes over REST and WebSocket. Pick the insights you want inside HA — rego status badges, next-service calendars, AI maintenance predictions.
- **Phase 2 (2027):** Full HACS custom integration with config flow: one-click install inside HA, entity setup for every vehicle, per-entity toggles, and a custom Lovelace card styled to match your HA theme.
- **Privacy first:** No raw telemetry leaves AutoBrain. Only processed insights — aggregated fuel costs, rego status, AI service predictions, charge-session summaries — are pushed. Your HA instance never sees raw OBD2 PIDs, live GPS routes, or anything you have not explicitly chosen to surface.

### Rollout FAQ

**Q: When does the Home Assistant integration ship?**
A: Phase 1 (REST + WebSocket feed) targets Q4 2026, with a closed beta opening in October. Phase 2 (full HACS custom integration with config flow) follows in 2027. Watch the public changelog and the AutoBrain #changelog channel for the day each phase lands.

**Q: What data does AutoBrain actually push to Home Assistant?**
A: Only processed insights you opt in to — service reminders, fuel efficiency and cost trends, rego status, and AI maintenance predictions. Raw OBD2 PIDs, live telemetry and GPS routes never leave AutoBrain unless you explicitly surface them.

**Q: Do I need new hardware?**
A: No. The integration runs on the same AutoBrain backend you already use — hosted or self-hosted. You just need a Home Assistant instance and a waitlist signup.

**Q: How do I join the beta?**
A: Email sales@autobrainservice.app with subject "HA waitlist" or join the waitlist below. Beta testers are picked from the waitlist first.

### CTA (bottom)

**Be the first to know.** Drop your email and we'll ping you the day the Home Assistant integration beta opens — one email, no marketing list, no spam.

Join the HA waitlist → (mailto:sales@autobrainservice.app?subject=HA%20waitlist)

Or watch the public changelog and the AutoBrain #changelog channel for the day the beta opens.