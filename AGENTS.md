# AGENTS.md — AutoBrain Marketing Website

Static marketing site for **AutoBrain**, deployed to Azure Static Web Apps at
`https://autobrainservice.app`. No build step, no framework, no package manager.
Plain HTML + `styles.css` + a few small JS files.

## Read this first

- **Everything is a static `.html` file at the repo root** (or in `blog/`). There
  is no build. If you add a page, add a `.html` file — nothing compiles it.
- **`changelog.html` is generated.** Do not hand-edit anything between the
  `<!-- CHANGELOG-START -->` and `<!-- CHANGELOG-END -->` markers; regenerate
  with `python3 scripts/gen_changelog.py` after editing `CHANGELOG.md`.
- **`CHANGELOG.md` is a mirror**, synced from `CannonFodder151/autobrain` by the
  `sync-changelog` job in that repo's `dockerhub-publish.yml` after every
  versioned deploy. Do not add website-only entries to it — those go in a
  separate website changelog or a Discord embed.
- **Security headers are in `staticwebapp.config.json`**, not in each page. The
  CSP is strict (`script-src 'self'` + Cloudflare Turnstile). Do not add inline
  `<script>` or third-party CSS/JS to any page without updating the CSP.
- **Contact form posts to n8n**, not to a form backend — see `lead.js` and the
  `form-action` in the CSP.

## Structure

| Path | What it is |
|------|-----------|
| `*.html` | Marketing pages (index, features, hosted, selfhost, about, contact, privacy, …) |
| `blog/*.html` | Long-form SEO posts (33 published) |
| `blog.html` | Blog index — must be updated when a post is added |
| `changelog.html` | Public release notes (generated, capped at 60 releases) |
| `changelog.md` / `CHANGELOG.md` | Release mirror (synced, full history kept on purpose) |
| `styles.css` | Single stylesheet, all pages |
| `nav.js`, `lead.js` | Theme toggle / mobile nav, contact form handler |
| `scripts/gen_changelog.py` | Regenerates the changelog blocks in `changelog.html` |
| `scripts/check_seo_drift.py` | Fails if a blog post is missing from blog.html/sitemap.xml/rss.xml |
| `docs/` | Positioning, launch checklists, SEO review |
| `.github/workflows/` | SWA deploy, sitemap submit, branch hygiene, SEO drift |
| `sitemap.xml`, `rss.xml`, `robots.txt` | SEO surface files |

## Workflow

1. Branch off `main`: `git checkout -b <issue>-description`
2. Make the change
3. If you touched `CHANGELOG.md`: `python3 scripts/gen_changelog.py`
4. If you added a blog post: add it to `blog.html`, `sitemap.xml`, and `rss.xml`
5. Push, open a PR, wait for QA + Security sign-off, then squash-merge
6. The merge auto-deploys to SWA — no manual deploy step

### Merging on this repo (read before merging)

This repo is **private on the GitHub Free plan**, so two GitHub features are
unavailable (verified AUT-4967, 2026-10-01):

| Feature | Status | Evidence |
|---|---|---|
| Branch protection / required reviews | Not available | `GET /branches/main/protection` → 403 "Upgrade to GitHub Pro or make this repository public" |
| Auto-merge (`allow_auto_merge`) | Not available | `PATCH /repos/... -d '{"allow_auto_merge":true}'` → HTTP 200 but field stays `false` |

Consequence: **do NOT use `gh pr merge --auto --squash` here.** It exits 0 and
prints nothing while doing nothing — `autoMergeRequest` stays `null`. That silent
no-op is the failure mode AUT-4967 was raised for.

**Merge explicitly instead**, once QA + Security have signed off on the PR:

```bash
gh pr merge <PR#> --repo CannonFodder151/autobrainservice-website --squash --delete-branch
```

Squash merge is permitted (`allow_squash_merge: true`) and needs no plan upgrade.
If it fails with a non-`UNSTABLE`/non-`BLOCKED` `mergeStateStatus`, mergeability
is a real signal — read `gh pr checks <PR#>` before retrying. The company-wide
rule "once QA and Security have approved a PR, squash-merge it immediately"
still applies; only the mechanism differs from `autobrain` and other public repos.

## SEO checklist for new pages

- `<title>` ≤ 60 chars, `<meta name="description">` ≤ 155 chars
- `<link rel="canonical" href="https://autobrainservice.app/<page>.html">`
- Open Graph + Twitter card tags (title, description, url, image)
- JSON-LD structured data: at minimum `WebPage` + `BreadcrumbList`
- `hreflang` alternates: `en-AU` + `x-default`
- Add to `sitemap.xml` with a realistic `<lastmod>`
- Add to the nav or a relevant hub page (orphan pages do not rank)
- `<meta name="robots" content="index, follow, max-image-preview:large">`

## Copy rules

- Australian English, "rego" not "registration" (unless explaining the legal term)
- Prices in AUD, always cite the monthly and annual figure
- Deterministic-first AI language: "works even when AI is down" is the core
  differentiator — see `docs/positioning.md`
- Never claim a feature is live when it is behind a "Coming soon" badge

## Related docs

- `docs/positioning.md` — messaging, pillars, content calendar
- `docs/petrol-price-map-launch-checklist.md` — launch readiness for the fuel map
- `docs/seo-review.md` — current SEO state and action items

<!-- graft:start -->
## Graft — repo context graph

This repo is indexed in `graft/`: small linked markdown nodes that explain each
system and carry exact file:line spans, kept in sync with the code through git.

For ANY task here — understanding how something works, finding where code lives,
or scoping a change — get context from the graph before grepping or opening
source files. Re-ask freely (it's cheap) and reuse literal identifiers you
already have (symbol, error string, file name) as the query. New to this repo?
Run `graft map` first — a token-budgeted orientation (dir clusters, hubs,
hotspots), no LLM, no key.

- Run `graft ask "<your question>" --source` → ranked nodes with the relevant
  code spans inlined (each hit's ≤8-line crux by default; `--full` for whole
  definitions when the crux isn't enough). Match the tool to the task shape:
  for understanding or editing, the top node IS the answer — cite its
  `covers:` file:line spans and edit straight from `--source`. For
  exhaustive tasks ("every occurrence / every caller of this pattern"), ranked
  results are top-N, not complete — run `graft grep "<literal>"` instead
  (exhaustive over indexed files, grouped by enclosing symbol), falling back
  to raw `grep -rn` only for unindexed files.
- `graft skeleton <file>` → every definition's signature + span, ~10× cheaper
  than reading the file; use it to skim an API surface.
- `graft callers <symbol>` gives precomputed, exact edges — who calls this.
  Add `--direction out` for what it calls, or `--depth N` to walk
  transitively for the full blast radius. For structural questions, skip
  ranking and use this directly.
- Or browse: `graft/INDEX.md` lists every node; follow the links.
- Monorepos and folders of multiple repos rank fairly across sub-projects —
  hits carry `[scope/]` labels naming which one's from. Narrow with
  `graft ask "<task>" --in <scope>/` once you know where you're working.

If a returned span is truncated ("+N more lines"), open the file at that exact
range before finalizing. Only open source files when a node genuinely lacks a
needed detail, and then at the exact file:line the node points to — never
re-read whole files.

After big code changes, refresh the graph with `graft build` (deterministic,
no API key, $0).
<!-- graft:end -->