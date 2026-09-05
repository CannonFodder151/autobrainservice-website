# AUT-2540 — High Availability Coming Soon Page Draft

> Human CMO approved via Discord `#marketing` (Parts 1-3) on 2026-09-05.
> This file is the source-of-truth content that was reviewed inline in Discord.
> The CMO approved the full content below — no further sign-off needed.

## Page: `/ha-coming-soon.html`

### Hero

**Headline:** AutoBrain Hosted Is Going High-Availability

**Subhead:** AutoBrain Hosted is migrating to Oracle Cloud Infrastructure — active/passive multi-zone deployment, automated failover, and zero-downtime rolling updates. The move starts late Q3 2026. We'll keep you posted every step of the way.

**CTA:** Be the first to know → [Notify me on launch] (mailto:sales@autobrainservice.app?subject=HA%20waitlist)

### What's changing

AutoBrain Hosted is moving off the current single-zone setup to Oracle Cloud Infrastructure (OCI) with a High-Availability architecture:

- **Multi-zone deployment** — primary + standby instances across two availability domains in the same region. If one zone goes down, traffic fails over automatically.
- **Zero-downtime updates** — rolling deployments mean no maintenance windows, no service interruption for subscribers.
- **Active/passive failover** — health checks every 30s; on failure, traffic routes to the standby within 60s. RTO < 5 min, RPO < 1 min.
- **Same features, same price** — the hosted experience you already use. No data migration needed; existing accounts and subscriptions carry over unchanged.

### Timeline

| Phase | Window | What's happening |
|-------|--------|-----------------|
| Planning & preparation | Late Q3 2026 | Infrastructure built in OCI, data sync test |
| Soft cutover (staging) | Early October 2026 | Canary traffic, final validation |
| Production cutover | Mid-October 2026 | DNS switch, monitoring ramp-up |
| Post-migration | October–November 2026 | Performance review, incident retrospectives |

### For existing subscribers

- **No action needed.** Your data, settings, and subscriptions stay exactly where they are.
- **No downtime.** The migration uses a phased cutover — you keep working through the entire process.
- **No price change.** All plans (Free, Enthusiast $5.90/mo, Garage $11.90/mo) stay the same.
- **Same support.** All existing support channels remain live.

### For new subscribers

- **Same plans.** Free tier plus Enthusiast and Garage paid plans — unchanged pricing and features.
- **Built for reliability.** The HA architecture is included in every hosted plan at no extra cost.

### FAQ

**Q: Will there be any downtime?**
A: No. The migration uses a phased cutover with redundant capacity. You stay logged in and working throughout.

**Q: Do I need to update my app or settings?**
A: No. The mobile app and web app continue to work exactly as before. No new app version or configuration required.

**Q: Is my data safe?**
A: Yes. All data is encrypted in transit (TLS 1.3) and at rest (AES-256). The migration copies data to the new region with per-record verification before the cutover.

**Q: Will the pricing change?**
A: No. All existing plans and prices remain the same. The HA architecture is included at no extra cost.

**Q: What if I self-host?**
A: Self-hosted AutoBrain is unaffected. The HA migration applies only to the managed AutoBrain Hosted service.

**Q: When exactly will this happen?**
A: Targeted for mid-October 2026. Sign up for launch notifications and we'll email you when the migration begins and completes.

### CTA (bottom)

**Ready for the update?** Drop your email and we'll send you a single migration status update — no marketing list.

[Be the first to know →](mailto:sales@autobrainservice.app?subject=HA%20waitlist)

Or watch the [public changelog](changelog.html) and the AutoBrain [#changelog](https://discord.com/channels/1397739559174053889/1426172943819493396) channel for live migration updates.
