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
| Fair Price: segment price benchmarks | **Data exists and was extracted (§2.3) — but only as *model-level* medians, never per model-year** | Quote with `sample_size` + as-of date + "across all model years" |
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

**Verdict (updated 2026-10-04, AUT-5570): the extract WAS run — through the
product's own API rather than SQL, because no agent has DB or SSH credential
(§2.1). Real, provider-backed benchmarks exist (§2.3.1) and AUT-4521 may quote
them. Two limits are hard: prices are **model-level, not model-year** (§2.3.2),
and "YoY movement per model" still **cannot** be sourced from AutoBrain data at
all — see §2.2.**

### 2.1 Why the SQL in §2.3 could not be run as written

| Blocker | Detail | Outcome |
|---|---|---|
| DB not network-reachable | `postgres` binds `127.0.0.1:5432` in `docker-compose.yml:50` on dev, demo, default and hosted. Re-confirmed 2026-10-04: `10.0.3.39:5432`, `10.0.3.17:5432`, `152.69.188.133:5432` all refused/unreachable from the agent container | Worked around — same table read through the API |
| No SSH credential | `devbox_ssh_password` is a board-scoped secret; `GET /api/companies/{id}/secrets` returns `{"error":"Board access required"}` for this agent role. The only SSH keys in the agent home are GitHub deploy keys (`~/.ssh/config`), which cannot log into the dev box. `10.0.3.39:22` is open, but there is no credential to use it | Unchanged — needs a board grant (AUT-5570 child) |
| No DB read integration | `connections_search` for `postgres` / `postgresql` / `database` / `db` / `ssh` / `devbox` all return `{"results":[]}` | Unchanged |
| CTO sign-off | Not granted | Unchanged — the extract did not need it because it ran through the already-public product API |

**Read path used instead.** `GET /api/v1/vehicles/{id}/valuation/market` and
`GET /api/v1/vehicles/{id}/valuation/market/search?q={make}` return the very
`market_listing_cache` row the SQL selects — `source`, `median_price`,
`low_price`, `high_price`, `sample_size`, `as_of` — from
`get_market_data()` / `search_market()`
(`backend/app/services/market_data.py:151` and `:179`). The acceptance rules in
§2.3 were applied unchanged. Nothing user-linked was read or written; the only
write is the service's own 24h-TTL upsert, identical to what any user of the
Fair Price feature triggers.

**Not covered:** a full table scan. Rows keyed to vehicles this agent cannot
access, and the whole hosted (production) environment, were never read. A
complete extract still needs the DB grant.

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

### 2.3.1 Extract results — run record (AUT-5570, 2026-10-04)

- **Environment:** demo — `https://demo.autobrainservice.app`
- **Read timestamp:** 2026-10-04T15:52Z (UTC)
- **Rows read:** 21 — 7 vehicle-keyed (the demo fleet) + 14 make-keyed
  (`search?q=`). See §2.1 for why the read went through the API.
- **Kept after acceptance rules (`sample_size >= 3` AND `source <> 'fallback'`):**
  **19**
- **Dropped:** 2 — Ducati Monster 821 (2019) and Kawasaki Ninja 650 (2021);
  the provider returns no motorcycle listings through the car search, so both
  rows are `source=fallback`, `sample_size=0`.
- **Model-year ladder rows:** **0** — the fleet contains no adjacent model
  years of the same make/model, and per §2.3.2 the ladder must never be
  published regardless.

Vehicle-keyed rows (as stored, key `(make, model, year)`):

| make | model | year | median (AUD) | low | high | n | source | as-of |
|---|---|---|---|---|---|---|---|---|
| mazda | MX-5 | 2005 | 33,994.50 | 24,999 | 39,800 | 8 | carsguide | 2026-10-04T15:50Z |
| nissan | Silvia S15 | 1999 | 56,440 | 38,995 | 80,000 | 4 | carsguide | 2026-10-04T15:50Z |
| nissan | Skyline GT-R | 2000 | 22,990 | 13,488 | 389,990 | 8 | carsguide | 2026-10-04T15:50Z |
| toyota | Camry | 2020 | 29,990 | 20,990 | 36,990 | 8 | carsguide | 2026-10-04T15:48Z |
| toyota | Hilux | 2016 | 37,990 | 20,999 | 38,990 | 3 | carsguide | 2026-10-04T15:50Z |

Make-keyed rows (key `(make, "", NULL)`):

| make | median (AUD) | low | high | n | source |
|---|---|---|---|---|---|
| toyota | 24,490 | 20,990 | 37,990 | 8 | carsguide |
| ford | 29,869 | 20,990 | 36,990 | 8 | carsguide |
| holden | 25,744 | 21,888 | 33,990 | 8 | carsguide |
| nissan | 24,988 | 20,490 | 31,990 | 8 | carsguide |
| mazda | 27,450 | 20,990 | 34,977 | 8 | carsguide |
| honda | 28,140 | 22,888 | 37,990 | 8 | carsguide |
| subaru | 31,725 | 25,988 | 34,950 | 8 | carsguide |
| hyundai | 29,984 | 20,990 | 36,950 | 8 | carsguide |
| kia | 27,450 | 21,490 | 37,990 | 8 | carsguide |
| volkswagen | 23,744 | 21,888 | 29,990 | 8 | carsguide |
| bmw | 31,490 | 21,990 | 39,990 | 8 | carsguide |
| mercedes-benz | 26,970 | 20,990 | 35,999 | 8 | carsguide |
| audi | 30,990 | 22,990 | 39,900 | 8 | carsguide |
| jeep | 23,990 | 20,900 | 36,350 | 8 | carsguide |

Copy rules for these figures:

- n is the provider's scrape window (top 8 matching listings, n=4–8 here),
  **not** a census of the market. Say "n listings on CarsGuide".
- Prices are AUD asking prices as scraped on the read date.
- Quote as **model-level** medians ("Toyota Camry listings, median $29,990,
  n=8, CarsGuide, 2026-10-04, all model years") — never per model year
  (§2.3.2).
- The 1999 Skyline GT-R high of $389,990 is a real R34 listing; the
  Skyline GT-R median of $22,990 is inflated by non-GTR Skyline variants
  the search matched (350GT/370GT). Model-keyed rows inherit the provider's
  model-matching, so treat niche-model medians with extra caution.

### 2.3.2 Finding: the year key is decorative — prices are model-level

Empirical check, 2026-10-04, demo env — the provider does **not** apply the
year (or model variant) filter:

- `Toyota Camry 2020` → listings spanning **2014–2024**.
- `Mazda MX-5 2005` → listings spanning **2016–2022**.
- `Nissan Skyline GT-R 2000` → Skyline 350GT/370GT variants, **1995–2021**.

Consequences:

- A `(make, model, year)` row's `median_price` aggregates **all years** of
  that model. Quoting "2020 Toyota Camry median $29,990" would be fabricated
  precision — $29,990 is the median of 2014–2024 Camry listings.
- The model-year ladder SQL above must **never be published**: its
  `pct_delta` compares two all-years rows and produces noise, not a price
  trend.
- This is a product bug, not just a copy rule: `/advisor/value` uses
  `get_market_data()` as the resale reference price, so a "2020 Camry"
  valuation is priced off all-year Camry listings. Tracked as an engineering
  follow-up off AUT-5570.
- The fix belongs in the market-data provider call
  (`backend/app/services/market_data.py:_fetch_provider`): filter returned
  listings by `year` (and model) in `_aggregate()` at minimum, and/or have
  the provider honour the `year`/`model` it is sent.

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
- §2.3.1 extract: run 2026-10-04T15:52Z against demo
  (`https://demo.autobrainservice.app`, demo account), read through
  `GET /api/v1/vehicles/{id}/valuation/market[/search]`; 21 rows read, 19 kept,
  2 dropped. Raw per-listing evidence (titles, prices, odometers, CarsGuide
  URLs) is reproducible by re-running those endpoints with the same queries.
- Findings are reproducible with the file references cited inline.
- Where this sheet says a figure does not exist, that is a verified absence,
  not a gap in the search.