#!/usr/bin/env python3
"""Tests for scripts/swa_preview_reclaim.py (AUT-4799).

Run: python3 scripts/test_swa_preview_reclaim.py
"""
import contextlib
import io
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("GITHUB_REPOSITORY", "CannonFodder151/autobrainservice-website")

import swa_preview_reclaim as spr  # noqa: E402

LIVE_URL = "https://brave-sand-02a651b10-141.centralus.7.azurestaticapps.net"
SECRET = "swa-token-should-never-appear-in-logs"
DEAD_URL = "https://brave-sand-02a651b10-136.centralus.7.azurestaticapps.net"


class TestStagingUrlFromComments(unittest.TestCase):
    def test_reads_swA_bot_comment(self):
        body = ("Azure Static Web Apps: Your stage site is ready! Visit it here: "
                + LIVE_URL + "\n")
        self.assertEqual(spr.staging_url_from_comments([{"body": body}]), LIVE_URL)

    def test_newest_comment_wins(self):
        old = {"body": "ready: " + DEAD_URL}
        new = {"body": "ready: " + LIVE_URL}
        self.assertEqual(spr.staging_url_from_comments([old, new]), LIVE_URL)

    def test_pr_without_preview_has_no_url(self):
        self.assertIsNone(spr.staging_url_from_comments([{"body": "no preview yet"}]))
        self.assertIsNone(spr.staging_url_from_comments([]))

    def test_ignores_trailing_punctuation(self):
        self.assertEqual(
            spr.staging_url_from_comments([{"body": "see " + LIVE_URL + "."}]),
            LIVE_URL,
        )

    def test_production_hostname_is_not_a_staging_url(self):
        # A PR comment quoting the production host must not read as a live slot
        # holder, or the reclaim step evicts a slot it does not need to.
        self.assertIsNone(spr.staging_url_from_comments(
            [{"body": "deployed to https://brave-sand-02a651b10.azurestaticapps.net/"}]))


class TestSelectVictims(unittest.TestCase):
    """The AUT-4799 failure: eviction must target PRs that hold a slot.

    Live shape on 2026-10-01: 8 open PRs, but only #123, #139 and #141 held a
    reachable staging URL - exactly the free-plan cap of 3.
    """

    def test_evicts_stalest_real_holder_not_stalest_open_pr(self):
        # The AUT-4827 rule evicted #123 here only because it ranked all open
        # PRs; #141 and #139 hold slots and must be kept.
        keep, victims = spr.select_victims([141, 139, 123], current_pr=140,
                                           preview_limit=3)
        self.assertEqual(keep, [141, 139])
        self.assertEqual(victims, [123])

    def test_envless_prs_are_never_candidates(self):
        # 122/131/132/133/140 are open but hold nothing, so they must not
        # appear in the eviction set at all.
        keep, victims = spr.select_victims([141, 139, 123], current_pr=140,
                                           preview_limit=3)
        self.assertNotIn(140, victims, "current PR was evicted")
        for envless in (122, 131, 132, 133, 140):
            self.assertNotIn(envless, victims)

    def test_current_pr_keeps_its_slot_even_as_stalest_holder(self):
        keep, victims = spr.select_victims([140, 139, 123], current_pr=140,
                                           preview_limit=3)
        self.assertNotIn(140, victims)
        self.assertEqual(victims, [], "3 holders at cap of 3 needs no eviction")

    def test_evicts_only_as_far_as_the_cap_requires(self):
        keep, victims = spr.select_victims([140, 139, 123, 100], current_pr=140,
                                           preview_limit=3)
        self.assertEqual(sorted(keep), [123, 139])
        self.assertEqual(victims, [100], "evicted a slot that was not needed")

    def test_far_over_cap_evicts_lru_first(self):
        keep, victims = spr.select_victims([7, 6, 5, 4, 3], current_pr=7,
                                           preview_limit=3)
        self.assertEqual(keep, [6, 5])
        self.assertEqual(victims, [4, 3])

    def test_no_holders_means_nothing_to_free(self):
        self.assertEqual(
            spr.select_victims([], current_pr=140, preview_limit=3), ([], []))


class TestAwaitRelease(unittest.TestCase):
    def test_returns_true_once_url_stops_serving(self):
        with mock.patch.object(spr, "serving", side_effect=[True, True, False]) as m, \
             mock.patch.object(spr.time, "sleep"):
            self.assertTrue(spr.await_release(LIVE_URL))
        self.assertEqual(m.call_count, 3)

    def test_gives_up_when_environment_never_tears_down(self):
        with mock.patch.object(spr, "serving", return_value=True), \
             mock.patch.object(spr.time, "sleep"), \
             mock.patch.object(spr.time, "time", side_effect=[0, 0, 999]):
            self.assertFalse(spr.await_release(LIVE_URL))

    def test_already_released_returns_immediately(self):
        with mock.patch.object(spr, "serving", return_value=False) as m, \
             mock.patch.object(spr.time, "sleep") as slp:
            self.assertTrue(spr.await_release(DEAD_URL))
        slp.assert_not_called()


class TestServing(unittest.TestCase):
    def test_http_error_is_not_serving(self):
        import urllib.error
        with mock.patch.object(spr.urllib.request, "urlopen",
                               side_effect=urllib.error.HTTPError(
                                   DEAD_URL, 404, "not found", {}, None)):
            self.assertFalse(spr.serving(DEAD_URL))

    def test_connection_error_is_not_serving(self):
        with mock.patch.object(spr.urllib.request, "urlopen",
                               side_effect=OSError("dns failure")):
            self.assertFalse(spr.serving("https://nope.azurestaticapps.net"))


class TestWorkflowContract(unittest.TestCase):
    """The step promise: a reclaim failure never skips the deploy (AUT-4983).

    main() only wraps the victim loop in try/finally, so a GhAuthError /
    URLError / missing env var raised earlier propagates and fails the step.
    Job-level continue-on-error only neutralises the job conclusion - the
    default `if: success()` guard still skips *Regenerate changelog* and
    *Build And Deploy*. Only step-level continue-on-error keeps that promise.
    """

    WF = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                      ".github", "workflows",
                      "azure-static-web-apps-happy-glacier-0f26af910.yml")

    def test_reclaim_step_has_step_level_continue_on_error(self):
        import yaml
        with open(self.WF) as fh:
            wf = yaml.safe_load(fh)
        job = wf["jobs"]["build_and_deploy_pr_job"]
        reclaim = [s for s in job["steps"] if s.get("name") == "Reclaim a preview slot"]
        self.assertEqual(len(reclaim), 1)
        self.assertIs(reclaim[0].get("continue-on-error"), True)
        # The trusted-script fetch is equally able to fail (the pathspec is
        # absent until this change merges once), and it sits before the deploy
        # steps, so it must not be allowed to skip them either.
        fetch = [s for s in job["steps"]
                 if s.get("name") == "Fetch trusted reclaim script"]
        self.assertEqual(len(fetch), 1)
        self.assertIs(fetch[0].get("continue-on-error"), True)
        # Upload must run on the default success() guard, not behind a skip.
        for name in ("Regenerate changelog", "Build And Deploy"):
            step = next(s for s in job["steps"] if s.get("name") == name)
            self.assertNotIn("if", step, f"{name} is guarded by an if: condition")


class TestTokenRedaction(unittest.TestCase):
    """R2: unfiltered client output must not carry the SWA token into the log."""

    def _run(self, detail):
        pr = {"number": 141, "head": {"repo": {"full_name": os.environ["GITHUB_REPOSITORY"]}}}
        env = {"CURRENT_PR": "140", "PREVIEW_LIMIT": "1",
               "GITHUB_WORKSPACE": tempfile.mkdtemp(prefix="swa-test")}
        spr._lines.clear()
        comments = [{"body": "Your stage site is ready! Visit it here: " + LIVE_URL}]
        with mock.patch.dict(os.environ, {**env, "SWA_TOKEN": SECRET}, clear=False), \
             mock.patch.object(spr, "_load_deps"), \
             mock.patch.object(spr, "_gh", side_effect=[[pr], comments]), \
             mock.patch.object(spr, "serving", return_value=True), \
             mock.patch.object(spr, "await_release", return_value=True), \
             mock.patch.object(spr, "_close_pr", return_value=("error", detail)), \
             contextlib.redirect_stdout(io.StringIO()):
            spr.main()
        return "\n".join(spr._lines)

    def test_token_is_redacted_from_reported_client_output(self):
        out = self._run("failed with token " + SECRET + " in the request")
        self.assertNotIn(SECRET, out)
        self.assertIn("***", out)

    def test_output_without_a_token_is_unchanged(self):
        out = self._run("BadRequest: maximum number of staging environments")
        self.assertIn("maximum number of staging environments", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)