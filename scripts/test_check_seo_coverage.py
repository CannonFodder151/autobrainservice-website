#!/usr/bin/env python3
"""Tests for the coverage-tile guard in scripts/check_seo_pages.py (AUT-5698).

The guard closed after petrol-price-map.html shipped a sentence that
contradicted the page's own tiles in three ways at once while the check
printed "OK: 63 pages clean". Each test below is one of those shapes, or
one of the near-misses that must stay clean — a guard that reports the
wrong state on correct copy gets deleted by the next person it blocks.

Run: python3 scripts/test_check_seo_coverage.py
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_seo_pages as csp  # noqa: E402


def page(tiles, prose):
    """A minimal page rendering `tiles` as status pills and `prose` in the body."""
    rows = "\n".join(
        f'<div class="state"><h3>{code}</h3>'
        f'<span class="status-pill status-{status}">'
        f'{"Live" if status == "live" else "Coming soon"}</span>'
        f"<p>{code} detail.</p></div>"
        for code, status in tiles
    )
    return (
        "<html><head><title>t</title></head><body>"
        f'<div class="state-grid">{rows}</div>'
        f"<p>{prose}</p>"
        "</body></html>"
    )


class TestCoverageTiles(unittest.TestCase):
    def test_status_comes_from_the_rendered_pill(self):
        html = page([("WA", "live"), ("VIC", "soon")], "")
        tiles, conflicts = csp.coverage_tiles(html)
        self.assertEqual(tiles, {"WA": "live", "VIC": "soon"})
        self.assertEqual(conflicts, [])

    def test_state_grid_is_not_itself_a_tile(self):
        """class="state-grid" contains "state"; only the token counts."""
        html = page([("WA", "live")], "")
        self.assertIn("state-grid", html)
        self.assertEqual(csp.coverage_tiles(html), ({"WA": "live"}, []))

    def test_same_state_both_statuses_is_a_contradiction(self):
        html = page([("QLD", "live"), ("QLD", "soon")], "")
        _, conflicts = csp.coverage_tiles(html)
        self.assertEqual(conflicts, ["QLD"])

    def test_a_page_with_no_tiles_claims_nothing(self):
        self.assertEqual(csp.coverage_tiles("<p>VIC is coming soon.</p>"), ({}, []))


class TestTileProseContradictions(unittest.TestCase):
    """Every one of these is a shape that shipped to production."""

    def _findings(self, tiles, prose):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "p.html").write_text(page(tiles, prose), encoding="utf-8")
            (root / "index.html").write_text("<p>home</p>", encoding="utf-8")
            (root / "rss.xml").write_text("<rss/>", encoding="utf-8")
            original, csp.ROOT = csp.ROOT, root
            try:
                return [f for f in csp.check_coverage_prose() if "p.html" in f]
            finally:
                csp.ROOT = original

    def test_soon_state_inside_a_live_claim(self):
        """AUT-5689 defect 2: "pulls live prices from ... VIC Servo Saver"."""
        found = self._findings(
            [("WA", "live"), ("VIC", "soon")],
            "The map pulls live prices from WA FuelWatch and VIC Servo Saver.",
        )
        self.assertTrue(any("VIC" in f and "live coverage" in f for f in found), found)

    def test_live_state_labelled_soon(self):
        """AUT-5689 defect 1: "(soon) QLD" while the QLD tile reads live."""
        found = self._findings(
            [("WA", "live"), ("QLD", "live")],
            "Live now in WA FuelWatch, (soon) QLD Fuel Prices.",
        )
        self.assertTrue(any("QLD" in f and "labelled soon" in f for f in found), found)

    def test_soon_marker_binds_to_its_own_state_only(self):
        """The defect sentence names three states. Reporting WA as well as
        QLD would be a false positive on correct copy elsewhere, so the
        window stays under the width of a neighbouring state's name."""
        found = self._findings(
            [("WA", "live"), ("QLD", "live"), ("VIC", "soon")],
            "Pulls live prices from WA FuelWatch, (soon) QLD Fuel Prices "
            "and VIC Servo Saver.",
        )
        self.assertTrue(any(f.startswith("p.html: QLD") for f in found), found)
        self.assertFalse(any(f.startswith("p.html: WA") for f in found), found)

    def test_state_written_out_in_full(self):
        found = self._findings(
            [("WA", "live"), ("VIC", "soon")],
            "The map pulls live prices from Victoria.",
        )
        self.assertTrue(any("VIC" in f for f in found), found)

    def test_soon_state_next_to_the_live_states_is_fine(self):
        """The fixed petrol-price-map.html:147 shape."""
        found = self._findings(
            [("WA", "live"), ("QLD", "live"), ("NSW", "soon"),
             ("ACT", "soon"), ("VIC", "soon")],
            "Pulls live prices from WA FuelWatch — the official government "
            "feed — and the QLD fuelpricesqld partner feed. NSW, ACT and VIC "
            "(Servo Saver) follow as their partner-feed keys are issued.",
        )
        self.assertEqual(found, [])

    def test_comma_spliced_live_and_soon_is_a_finding(self):
        """Rule 1 is sentence-granular, not clause-granular: a comma
        cannot carry the attribution a semicolon can. "live in WA, NSW
        is coming soon" reads as NSW being live, so it is reported —
        write the two claims as separate sentences to stay clean."""
        found = self._findings(
            [("WA", "live"), ("NSW", "soon")],
            "The map is live in WA, NSW is coming soon.",
        )
        self.assertTrue(any("NSW" in f for f in found), found)

    def test_states_with_no_tile_are_not_judged(self):
        found = self._findings(
            [("WA", "live"), ("VIC", "soon")],
            "Live today in WA and QLD; SA and NT have no free feed.",
        )
        self.assertEqual(found, [])


class TestBlockBoundaries(unittest.TestCase):
    """Adjacent blocks must not concatenate into one sentence, or a tile's
    "Coming soon" inherits the live claim written in the paragraph above it."""

    def test_paragraphs_do_not_merge(self):
        html = (
            "<html><body><p>The map is live in WA and QLD.</p>"
            '<div class="state"><h3>VIC</h3>'
            '<span class="status-pill status-soon">Coming soon</span></div>'
            "</body></html>"
        )
        self.assertIn("VIC.", csp.body_prose(html))
        self.assertNotIn("QLD. VIC", csp.body_prose(html))

    def test_head_metadata_is_not_body_prose(self):
        html = (
            '<html><head><meta name="description" content="Live prices in '
            'WA and VIC"></head><body><p>Hi</p></body></html>'
        )
        self.assertEqual(csp.body_prose(html), "Hi.")


class TestPartnerProvenance(unittest.TestCase):
    """AUT-5689 defect 3: a partner feed inside "the official state
    fuel-price feeds"."""

    def _findings(self, prose):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "p.html").write_text(
                f"<html><body><p>{prose}</p></body></html>", encoding="utf-8"
            )
            (root / "rss.xml").write_text("<rss/>", encoding="utf-8")
            original, csp.ROOT = csp.ROOT, root
            try:
                return csp.check_partner_provenance()
            finally:
                csp.ROOT = original

    def test_partner_feed_called_official(self):
        found = self._findings(
            "Pulls live prices from the official state fuel-price feeds — "
            "WA FuelWatch, QLD Fuel Prices and VIC Servo Saver."
        )
        self.assertTrue(any("servo saver" in f for f in found), found)

    def test_partner_feed_labelled_partner_in_the_same_sentence(self):
        found = self._findings(
            "Coverage is WA via the official government feed and QLD via the "
            "fuelpricesqld partner feed."
        )
        self.assertEqual(found, [])

    def test_paid_aggregator_named_without_official_is_fine(self):
        found = self._findings(
            "Full coverage needs a paid aggregator (PetrolSpy / Informed "
            "Sources / MotorMouth)."
        )
        self.assertEqual(found, [])

    def test_official_claim_with_no_partner_source_is_fine(self):
        found = self._findings(
            "SA, TAS and NT don't have a free official fuel-price feed."
        )
        self.assertEqual(found, [])

    def test_runs_without_tiles(self):
        """The partner rule is a sentence-level claim: it must fire on a
        page that renders no coverage tiles at all."""
        self.assertTrue(self._findings(
            "Servo Saver is our official VIC feed."
        ))


class TestShippedPage(unittest.TestCase):
    """petrol-price-map.html is the page this guard exists for. Reading it
    here means a future rewrite of the tiles alone cannot silently make the
    prose contradictory again."""

    def test_coverage_prose_agrees_with_the_tiles(self):
        tiles, conflicts = csp.coverage_tiles(
            (csp.ROOT / "petrol-price-map.html").read_text(encoding="utf-8")
        )
        self.assertEqual(conflicts, [])
        self.assertEqual(tiles["WA"], "live")
        self.assertEqual(tiles["QLD"], "live")
        self.assertEqual(tiles["VIC"], "soon")
        self.assertEqual(csp.check_coverage_prose(), [])
        self.assertEqual(csp.check_partner_provenance(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)