# Approval-gated automerge

`CannonFodder151` private repos run on the free GitHub plan, where
`allow_auto_merge` cannot be enabled (GitHub Pro required). `.github/workflows/automerge.yml`
replaces it: the workflow performs the squash-merge itself, deterministically,
once every gate below passes. Same behaviour as GitHub native auto-merge,
no plan dependency.

Ported from `CannonFodder151/autobrain-shop-website` (merge `9b3e86f3`, PR #22).

## Gates

A PR is squash-merged only when **all** of these hold:

| Gate | Check |
| --- | --- |
| Default branch | `.base.ref` equals the repo default branch |
| Not a draft | `.draft` is not `true` |
| Mergeable | `.mergeable_state` is `clean` |
| Based on base | `GET /compare/{default}...{head.sha}` returns `status: ahead` |
| Approved | latest review from a non-author is `APPROVED` |
| No hold | no `hold` label on the PR |
| Green | every status check is `SUCCESS`, `SKIPPED` or `NEUTRAL`, and none still pending |

Anything else logs `skip: <reason>` and exits 0. The workflow never force-merges.

## Based on base

A squash merge takes the **head tree wholesale** — it does not replay the branch's
commits onto the base. So a head that does not contain the current base tip
silently *deletes* every base commit the head is missing. GitHub reports such a
head as `mergeable_state: clean` (a squash is always conflict-free), so the other
gates do not catch it.

That is how PR #152 wiped `main` to a single file on 2026-10-03: head
`ci/aut-5336-automerge-workflow` shared no ancestor with `main`, so merging it
reduced the tree to that branch's one file (AUT-5339).

The gate therefore requires the compare status to be exactly `ahead`, meaning
the base tip is an ancestor of the head. `diverged`, `behind` and `identical` are
all rejected, as is any unreadable compare response — it fails closed. A stale
branch is not "wrong", it is just not ready: merge the default branch into it and
the status becomes `ahead` and it merges on the next trigger.

```
skip: head <sha> is not based on current main (compare status=diverged ahead_by=1 behind_by=2) — merge main into the head branch first
```

The merge itself also passes `--match-head-commit`, so a force-push between the
gate and the merge aborts instead of merging a head that was never checked.

## Verifying the gates

```bash
python3 scripts/test_automerge_gate.py
```

Runs the workflow's real `run:` block against a stub `gh`: an orphan head, a
diverged head, a head behind base, an identical head and a failed compare are all
refused; a normal PR merges. No PRs pushed, no approvals spent.

## Triggers

`pull_request_review` (submitted), `pull_request` (ready_for_review),
`check_run` (completed), `status`. The job is skipped for its own `check_run`
named `automerge` to avoid recursion.

## Hold

```bash
gh pr edit <PR> --add-label hold
```

Dismisses the merge without closing the PR.

## Review identity caveat

The approval gate requires a review from an account **other than the PR author**.
Agents in this company author PRs as `CannonFodder151`, so an approval submitted
from that same account is filtered out and the PR will not auto-merge.
GitHub also blocks a self-approval outright (`422 Can not approve your own pull
request`), and `GITHUB_TOKEN` cannot create or approve PRs on these repos
(`403 GitHub Actions is not permitted to create or approve pull requests` — the
"Allow GitHub Actions to create and approve pull requests" repo setting is off
and not REST-toggleable). A second, non-author approving identity (or that
setting enabled) is therefore required to exercise the gate end-to-end.

Refs: AUT-2230, AUT-5328, AUT-5336