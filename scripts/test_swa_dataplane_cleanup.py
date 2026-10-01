#!/usr/bin/env python3
"""Self-check for scripts/swa_dataplane_cleanup.py (AUT-4961).

Proves the two behaviours the 2026-10-01 outage fix relies on:
  1. _gh() retries transient 429/502/503/504 + connection errors, and does NOT
     retry 401/403.
  2. main() records a per-PR failure and keeps sweeping instead of aborting.

Run: python3 scripts/test_swa_dataplane_cleanup.py
"""
import io
import json
import os
import sys
import urllib.error
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("GITHUB_REPOSITORY", "CannonFodder151/autobrainservice-website")
os.environ.setdefault("GITHUB_TOKEN", "test-token")

import swa_dataplane_cleanup as swc  # noqa: E402


def _http_error(code, headers=None):
    hdrs = headers or {}
    return urllib.error.HTTPError(
        "https://api.github.com/x", code, f"err {code}", hdrs, io.BytesIO(b"")
    )


def _response(payload):
    r = mock.MagicMock()
    r.read.return_value = json.dumps(payload).encode()
    r.__enter__ = lambda s: r
    r.__exit__ = lambda s, *a: False
    return r


class TestGhRetry(unittest.TestCase):
    def _run(self, side_effect, attempts):
        with mock.patch.object(swc.urllib.request, "urlopen", side_effect=side_effect) as m, \
             mock.patch.object(swc.time, "sleep"):
            return swc._gh("/pulls/1"), m

    def test_retries_503_then_succeeds(self):
        payload, m = self._run([_http_error(503), _response({"number": 1})], 2)
        self.assertEqual(payload, {"number": 1})
        self.assertEqual(m.call_count, 2)

    def test_gives_up_after_max_attempts(self):
        with mock.patch.object(swc.urllib.request, "urlopen", side_effect=_http_error(503)) as m, \
             mock.patch.object(swc.time, "sleep"):
            with self.assertRaises(urllib.error.HTTPError):
                swc._gh("/pulls/1")
        self.assertEqual(m.call_count, swc.GH_ATTEMPTS)

    def test_respects_retry_after_header(self):
        delays = []
        with mock.patch.object(
            swc.urllib.request, "urlopen",
            side_effect=[_http_error(429, {"Retry-After": "7"}), _response({})],
        ), mock.patch.object(swc.time, "sleep", side_effect=delays.append):
            swc._gh("/pulls/1")
        self.assertEqual(len(delays), 1)
        self.assertGreaterEqual(delays[0], 7.0)

    def test_retries_connection_error(self):
        payload, m = self._run([urllib.error.URLError("conn reset"), _response({"ok": True})], 2)
        self.assertEqual(payload, {"ok": True})
        self.assertEqual(m.call_count, 2)

    def test_auth_error_is_fatal_and_not_retried(self):
        with mock.patch.object(swc.urllib.request, "urlopen", side_effect=_http_error(401)) as m:
            with self.assertRaises(swc.GhAuthError):
                swc._gh("/pulls/1")
        self.assertEqual(m.call_count, 1)

    def test_404_is_not_retried(self):
        with mock.patch.object(swc.urllib.request, "urlopen", side_effect=_http_error(404)) as m:
            with self.assertRaises(urllib.error.HTTPError):
                swc._gh("/pulls/999999")
        self.assertEqual(m.call_count, 1)


class TestSweepContinues(unittest.TestCase):
    def test_one_bad_pr_does_not_abort_the_sweep(self):
        calls = []

        def fake_close(n, ws):
            calls.append(n)
            if n == 2:
                raise urllib.error.HTTPError("u", 503, "Service Unavailable", {}, io.BytesIO(b""))
            return "ok", ""

        with mock.patch.object(swc, "_fetch_closed_prs", return_value=[1, 2, 3]), \
             mock.patch.object(swc, "_close_pr", side_effect=fake_close), \
             mock.patch.object(swc, "DRY", False), \
             mock.patch.object(swc, "SWA_TOKEN", "tok"), \
             mock.patch.dict(os.environ, {"GITHUB_WORKSPACE": "/tmp"}), \
             mock.patch.object(swc.shutil, "rmtree"):
            rc = swc.main()
        self.assertEqual(calls, [1, 2, 3])
        self.assertEqual(rc, 0)

    def test_404_is_skipped_not_errored(self):
        with mock.patch.object(swc, "_fetch_closed_prs", return_value=[1]), \
             mock.patch.object(swc, "_close_pr", side_effect=_http_error(404)), \
             mock.patch.object(swc, "DRY", False), \
             mock.patch.object(swc, "SWA_TOKEN", "tok"), \
             mock.patch.dict(os.environ, {"GITHUB_WORKSPACE": "/tmp"}), \
             mock.patch.object(swc.shutil, "rmtree"):
            self.assertEqual(swc.main(), 0)

    def test_auth_failure_mid_sweep_aborts(self):
        calls = []

        def fake_close(n, ws):
            calls.append(n)
            if n == 2:
                raise swc.GhAuthError("GitHub API 403 on /pulls/2")
            return "ok", ""

        with mock.patch.object(swc, "_fetch_closed_prs", return_value=[1, 2, 3]), \
             mock.patch.object(swc, "_close_pr", side_effect=fake_close), \
             mock.patch.object(swc, "DRY", False), \
             mock.patch.object(swc, "SWA_TOKEN", "tok"), \
             mock.patch.dict(os.environ, {"GITHUB_WORKSPACE": "/tmp"}), \
             mock.patch.object(swc.shutil, "rmtree"):
            rc = swc.main()
        self.assertEqual(rc, 1)
        self.assertEqual(calls, [1, 2])


if __name__ == "__main__":
    unittest.main(verbosity=2)