#!/usr/bin/env python3
"""Tests for scripts/check_seo_pages.py and scripts/generate_rss.py (AUT-5577).

Run: python3 scripts/test_check_seo_pages.py
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check_seo_pages as csp  # noqa: E402
import generate_rss  # noqa: E402


class TestAccordionQuestions(unittest.TestCase):
    """The guard fails open on two valid HTML5 shapes (AUT-5577): a page
    rendering either one produced no collected questions, so check_faq_parity
    skipped it and the FAQPage JSON-LD was never compared against the visible
    FAQ. Both must be collected."""

    def test_lowercase_baseline_still_matches(self):
        self.assertEqual(
            csp.accordion_questions(
                "<details><summary>How long?</summary><p>A while.</p></details>"
            ),
            ["How long?"],
        )

    def test_uppercase_details_is_the_same_element(self):
        self.assertEqual(
            csp.accordion_questions(
                "<DETAILS><SUMMARY>How long?</SUMMARY><p>A while.</p></DETAILS>"
            ),
            ["How long?"],
        )

    def test_mixed_case_with_attributes(self):
        self.assertEqual(
            csp.accordion_questions(
                '<Details class="faq"><SUMMARY open>How long?</Summary></Details>'
            ),
            ["How long?"],
        )

    def test_content_before_summary(self):
        self.assertEqual(
            csp.accordion_questions(
                "<details><p>Tap to expand</p><summary>How long?</summary>"
                "<p>A while.</p></details>"
            ),
            ["How long?"],
        )

    def test_unlabelled_details_does_not_absorb_the_next_question(self):
        """A <details> with no <summary> must not swallow a later one and
        report a phantom parity failure."""
        self.assertEqual(
            csp.accordion_questions(
                "<details><p>No question here</p></details>"
                "<details><summary>How long?</summary><p>A while.</p></details>"
            ),
            ["How long?"],
        )

    def test_question_text_is_stripped_of_markup(self):
        self.assertEqual(
            csp.accordion_questions(
                "<DETAILS><SUMMARY><strong>How <em>long</em>?</strong></SUMMARY>"
                "text</DETAILS>"
            ),
            ["How long?"],
        )


class TestFaqParityFailsClosed(unittest.TestCase):
    """A visible FAQ the guard can read must be compared, not skipped."""

    def test_uppercase_accordion_with_no_jsonld_is_a_finding(self):
        page = (
            "<html><body><script type='application/ld+json'>"
            '{"@type": "FAQPage", "mainEntity": []}'
            "</script><DETAILS><SUMMARY>How long?</SUMMARY>"
            "<p>A while.</p></DETAILS></body></html>"
        )
        self.assertEqual(csp.accordion_questions(page), ["How long?"])


class TestCredentialGuard(unittest.TestCase):
    def test_email_adjacent_token_still_caught(self):
        self.assertTrue(csp.CREDENTIAL_LITERAL.search("demo@autobrainservice.app / demo"))

    def test_bare_password_literal_caught(self):
        self.assertTrue(csp.CREDENTIAL_ASSIGNMENT.search("<p>password: hunter2</p>"))

    def test_quoted_assignment_caught(self):
        self.assertTrue(csp.CREDENTIAL_ASSIGNMENT.search('"api_key": "sk-live-abc123"'))

    def test_prose_is_not_a_finding(self):
        self.assertIsNone(csp.CREDENTIAL_ASSIGNMENT.search("Your password must be unique"))

    def test_login_form_label_is_not_a_finding(self):
        self.assertIsNone(
            csp.CREDENTIAL_ASSIGNMENT.search(
                '<label for="pw">Password:</label><input id="pw" type="password">'
            )
        )


class TestRssIsCwdIndependent(unittest.TestCase):
    def test_reads_blog_html_from_repo_root_not_cwd(self):
        card = (
            '<article class="card blog-card u-inherit">'
            '<span class="date">3 September 2026 · 4 min</span>'
            "<h3><a href=\"blog/x.html\">X</a></h3><p>Desc.</p></article>"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "blog.html").write_text(
                f"<html><body>{card}</body></html>", encoding="utf-8"
            )
            original_root, original_cwd = generate_rss.ROOT, os.getcwd()
            try:
                generate_rss.ROOT = root
                os.chdir(tmp)  # same directory: a relative open would still pass
                generate_rss.main()
            finally:
                generate_rss.ROOT = original_root
                os.chdir(original_cwd)
            self.assertIn("<title>X</title>", (root / "rss.xml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)