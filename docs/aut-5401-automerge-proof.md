# AUT-5401 automerge proof

E2E evidence that `.github/workflows/automerge.yml` squash-merges a PR
authorised by a Paperclip approval-marker comment, with no human running
`gh pr merge`. The PR is merged by the workflow's own `GITHUB_TOKEN`
(`mergedBy: app/github-actions`), not by the PR author and not by a person.

Run logs and the two refusal/approval cases are recorded on AUT-5401.
