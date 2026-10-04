# Sourced Data Sheet — AUT-5545 (for AUT-4521 / AUT-4422)

**Owner:** Founding Engineer · **Date:** 2026-10-04 · **Blocks:** [AUT-4521](/AUT/issues/AUT-4521)

## How to use this sheet

Every number in the AUT-4422 content batch must either trace to a row in this
sheet or be deleted. This sheet records what AutoBrain can and cannot honestly
claim today. It is deliberately explicit where a figure does not exist, because
the correct outcome for a missing figure is **cut the claim**, not estimate it.

| AUT-4521 item | Verdict | Action |
|---|---|---|
| OBD2: "12 adapters tested, 3 passed, 2 bricked" | **No data exists. Fabricated.** | Cut the claim entirely |
| OBD2: vehicle test fleet | **No data exists.** | Cut the claim entirely |
| OBD2: adapter prices / picks | Unsourced editorial | Label as opinion, or source externally |
| Fair Price: segment price benchmarks | **Data exists but not read yet** | Needs one DB read (spec in §2.3) |
| Fair Price: YoY movement per model | **Not derivable from AutoBrain data at all** | Cut, or attribute to a named external index |
| Fair Price: state transfer costs | Not engineering-owned | CMO to source from state govt sites |

---

## 1. OBD2 adapter test results — the data does not exist

**Verdict: no adapter test programme has ever been run. There is no pass/fail/
brick record anywhere in AutoBrain engineering. The drafted claim must be cut.**

### 1.1 What was searched

| Source | Result |
|---|---|
| `CannonFodder151/autobrain` (repo-wide, incl. `docs/`, `firmware/`, `backend/`) | Zero adapter-test records. The only "brick" hits are "a laptop brick + barrel plug works" as a bench PSU (`docs/Engineering/obd2-dongle/nodemcu32s-build-guide.md:425`) |
| `CannonFodder151/autobrain-mobile` (repo-wide) | Zero adapter-test records |
| Paperclip issue tracker | No test-fleet or adapter-bench issue exists |
| Outline (`2026-W33 OBD Dongle Research`, AUT-363) | Build-vs-buy research memo, not a test log |

### 1.2 Why no test data exists — three independent reasons

1. **Generic ELM327 adapters are no longer supported at all.**
   [AUT-427](https://github.com/CannonFodder151/autobrain) removed support for
   generic ELM327 adapters (VGate iCar Pro, OBDLink, etc.); only the
   custom-built AutoBrain OBD2 adapter is supported
   (`docs/Engineering/obd-integration.md:5`). The company is not testing
   third-party adapters — it stopped shipping that path.

2. **The AutoBrain dongle is still pre-prototype.**
   "Hardware: BOM ordered; prototype build tracked in AUT-386"
   (`docs/Engineering/obd2-dongle/README.md:34`). Firmware is compile-verified
   (`pio run`) and the host self-check passes, but **no prototype has been
   built or bench-tested**.

3. **The only third-party adapter ever used was a single unit, informally.**
   VGate iCar Pro, used as a leave-in trip logger (AUT-362). One unit in
   practice is not a test fleet and has no pass/fail/brick record.

### 1.3 What OBD2 testing AutoBrain *can* honestly claim today

All test coverage is software coverage with **zero hardware in the loop**:

| Test file | Tests | What it actually verifies |
|---|---|---|
| `mobile/test/obd_trip_recorder_test.dart` | 19 | Ignition/trip state machine against synthetic PIDs (hysteresis, link-drop, persistence) |
| `mobile/test/dongle_provisioning_test.dart` | 12 | Dongle WiFi provisioning flow |
| `mobile/test/dongle_settings_test.dart` | 2 | Dongle settings state |
| `mobile/test/dongle_wifi_screen_test.dart` | 4 | Dongle WiFi screen widget behaviour |
| `mobile/test/car_kit_trip_monitor_test.dart` | 8 | Car-kit trip monitor orchestration |
| **Total** | **45** | **Automated logic tests, no adapter or dongle hardware** |

Suggested replacement sentence for the OBD2 blog (fully supported):
> "Our OBD2 trip-recording logic is covered by 45 automated tests. The dongle
> itself is a custom unit still in prototype — we don't buy or endorse
> third-party adapters, and we don't test other people's hardware."

### 1.4 Second unsupported claim found in the published buying guide

`blog/obd2-adapter-buying-guide-2026.html` (published 2026-10-03) carries two
implied-test claims that this sheet cannot source:

- The table header **"TL;DR — our tested picks"** implies AutoBrain bench-tested
  these five adapters. No such testing happened (§1.1). Reword to
  "our picks" / "recommended picks", or run a real test programme and record
  results here first.
- **"Bricks if you attempt a firmware update (common with clones)"** — this is
  a real-world claim with no source in AutoBrain engineering. Either cite a
  published source (name + URL + retrieval date) or cut the sentence.

---

## 2. Fair-value benchmark extract

**Verdict: the extract was NOT produced in this run — valuation DB read access
was not available to the agent that owns this work. The segment benchmarks must
be cut from copy until the extract in §2.3 is run. Separately, "YoY movement per
model" cannot be sourced from AutoBrain data *at all* — see §2.2.**

### 2.1 Why no extract was produced

| Blocker | Detail |
|---|---|
| DB not network-reachable | `postgres` binds `127.0.0.1:5432` in `docker-compose.yml:50` on dev, demo, default and hosted. Confirmed unreachable on 10.0.3.39, 10.0.3.17, 152.69.188.133 |
| No SSH credential | The `devbox_ssh_password` secret was not readable to this agent's run, so the dev box could not be entered |
| No DB read integration | No PostgreSQL connection exists for this agent (`connections_search` → no results) |
| Escalation path | The Paperclip control plane became unresponsive during this run, so the CTO sign-off/grant could not be raised in-thread. This is the open item |

### 2.2 Finding: "YoY movement per model" is not derivable from AutoBrain data

This matters beyond access: **the AutoBrain valuation data model stores no
market price history**, so no YoY series can ever be extracted from it.

- `market_listing_cache` (`backend/app/models/market_listing.py`) holds **one
  row per `(make, model, year)`** — enforced by
  `UniqueConstraint("make", "model", "year")`.
- `_store()` (`backend/app/services/market_data.py:248-264`) **overwrites** that
  row's `median_price`/`low_price`/`high_price`/`sample_size` on every refresh
  and stamps `fetched_at`. No previous value is retained.
- Freshness window is `CACHE_TTL_HOURS = 24`
  (`backend/app/services/market_data.py:27`).
- `valuation_snapshots` (`backend/app/models/valuation.py`) *does* have a
  `created_at` history, but it records **AutoBrain's own per-vehicle estimate**,
  not an independent market series. YoY from it would measure our own model
  drift, not the market, and it is per-vehicle (user-linked) data.

Consequences for copy:

- ✅ **Available:** a *current* cross-section — median/low/high price per
  `(make, model, year)` with sample size and provider, as of a stated timestamp.
- ❌ **Never available:** a price trend, YoY movement, "prices fell 8% last year",
  or any month-over-month claim attributed to AutoBrain. AutoBrain does not
  store history.
- If the CMO wants a YoY market claim, it must be attributed to a **named
  external index** (publisher + report title + URL + retrieval date) — never to
  "AutoBrain data".

### 2.3 Extract spec — one read, ready to run

Run on whichever environment holds the data, read-only, aggregate only. No
`vehicle_id` / user data is selected.

```sql
-- Current segment price benchmark cross-section.
-- Acceptance rules: keep only provider-backed rows with a usable sample;
-- row is only publishable if sample_size >= 3.
WITH m AS (
  SELECT make, model, year, median_price, low_price, high_price,
         sample_size, source, fetched_at
  FROM market_listing_cache
  WHERE median_price IS NOT NULL
)
SELECT make, model, year,
       median_price, low_price, high_price, sample_size, source,
       fetched_at,
       CASE WHEN sample_size >= 3 THEN 'publishable' ELSE 'too-thin' END AS usable
FROM m
ORDER BY make, model, year;
```

Model-year ladder (a cross-section, **not** a trend — label it as such):

```sql
-- Same make/model, adjacent model years. This is a price ladder across model
-- years, NOT year-on-year movement of one model. Never present as YoY.
WITH m AS (
  SELECT make, model, year, median_price, sample_size, source, fetched_at
  FROM market_listing_cache
  WHERE median_price IS NOT NULL AND sample_size >= 3 AND source <> 'fallback'
)
SELECT cur.make, cur.model, cur.year,
       cur.median_price  AS price_this_year,
       prev.median_price AS price_prev_year,
       round(((cur.median_price - prev.median_price)
              / NULLIF(prev.median_price, 0) * 100)::numeric, 1) AS pct_delta,
       cur.sample_size, cur.source, cur.fetched_at
FROM m cur
LEFT JOIN m prev
  ON prev.make = cur.make AND prev.model = cur.model
 AND prev.year = cur.year - 1
ORDER BY cur.make, cur.model, cur.year;
```

Rules for whoever runs it:

1. Record the environment, the timestamp of the read, and the row counts.
2. Only `sample_size >= 3` rows may be quoted; `source = 'fallback'` rows are
   not real market data (the pipeline fabricates a deterministic estimate).
3. Add `sample_size` and `fetched_at` next to any price quoted in copy.
4. Post the result as a comment on [AUT-5545](/AUT/issues/AUT-5545) and append
   the results table to this file, then unblock
   [AUT-4521](/AUT/issues/AUT-4521).

### 2.4 State of the published Fair Price blog

`blog/fair-price-used-car-2026.html` (published 2026-10-01) contains **no
AutoBrain valuation figures at all** — it is generic RedBook/CarsGuide buying
advice. However, its price-impact ranges ("-15-25%", "$400-800", "$800-1,500")
are editorial judgment with no source in this sheet. Either source them
externally, or keep them as clearly-labelled opinion ("typical", "rough rule of
thumb") rather than presented data.

---

## Provenance

- Repos inspected at commit: `autobrain` `main`, `autobrain-mobile`
  `b3678a9`, `autobrainservice-website` `main`.
- Findings are reproducible with the file references cited inline.
- Where this sheet says a figure does not exist, that is a verified absence,
  not a gap in the search.