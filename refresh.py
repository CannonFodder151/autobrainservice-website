#!/usr/bin/env python3
"""Apply Phase 1 marketing copy refresh to website HTML files."""
import re, pathlib

ROOT = pathlib.Path("/tmp/paperclip-run-aut-3968-798fbbae-24a-1rzlnK/autobrainservice-website")

# (file, old, new) replacements — old/new are literal strings
edits = [
    # ---- hosted.html ----
    ("hosted.html",
     "Hosted Plans & Pricing — AutoBrain | AI Car Companion from $5.90/mo",
     "Hosted Plans & Pricing — AutoBrain | Reliable Car Companion from $5.90/mo"),
    ("hosted.html",
     "AutoBrain hosted plans — Free, Enthusiast $5.90/mo (7-day free trial) or $59/yr, Garage $11.90/mo (7-day free trial) or $119/yr. All AI features included, private and reliable with no lock-in.",
     "AutoBrain hosted plans — Free, Enthusiast $5.90/mo (7-day free trial) or $59/yr, Garage $11.90/mo (7-day free trial) or $119/yr. All AI features included, running on a simplified, consolidated stack with deterministic fallbacks."),
    # ---- selfhost.html ----
    ("selfhost.html",
     "Run AutoBrain on your own server for free. MIT-licensed, full control over your data. Service reminders, fuel tracking, rego lookup and more.",
     "Run AutoBrain on your own server for free. MIT-licensed, full control over your data. Service reminders, fuel tracking, rego lookup and more — with a leaner container stack and deterministic-first AI."),
    ("selfhost.html",
     "Run AutoBrain on your own server. Full control, your data stays yours. Free forever under MIT license.",
     "Run AutoBrain on your own server. Full control, your data stays yours. Free forever under MIT license — fewer containers, faster startup, and AI that works even when the router is down."),
    ("selfhost.html",
     "Run AutoBrain on your own server. Free forever, no lock-in.",
     "Run AutoBrain on your own server. Free forever, no lock-in."),
    # ---- about.html ----
    ("about.html",
     "The story behind AutoBrain — built by Nathan, an IT professional and car enthusiast who wanted a smarter way to look after his own cars. Open source (MIT), self-hostable or hosted.",
     "The story behind AutoBrain — built by Nathan, an IT professional and car enthusiast who wanted a smarter way to look after his own cars. Open source (MIT), self-hostable or hosted. Phase 1 rewrote the core for reliability: fewer containers, vectorised records, deterministic-first AI, and docs that stay in sync with the code."),
    ("about.html",
     "The story behind AutoBrain — built by Nathan, an IT professional who wanted a smarter way to look after his own cars.",
     "The story behind AutoBrain — built by Nathan, an IT professional who wanted a smarter way to look after his own cars. Phase 1 rewrote the core for reliability: fewer containers, vectorised records, deterministic-first AI."),
    # ---- features.html meta ----
    ("features.html",
     "Every AutoBrain feature: predictive maintenance, fuel intelligence, AI diagnostics, receipt & parts scanning, inventory, Australian rego lookup, Rego Status (paid), resale estimates, Home Assistant integration (coming soon), Electric Spy, EV Log Book and PHEV support (coming soon).",
     "Every AutoBrain feature: predictive maintenance, fuel intelligence, AI diagnostics, receipt & parts scanning, inventory, Australian rego lookup, Rego Status (paid), resale estimates, Home Assistant integration (Phase 1 live), Electric Spy, EV Log Book and PHEV support (coming soon). Deterministic-first AI keeps insights available when the router is down."),
    ("features.html",
     "Predictive maintenance, fuel intelligence, AI diagnostics, receipt & parts scanning, inventory, rego lookup, Rego Status (paid), resale estimates, Home Assistant integration (Phase 1 live, Phase 2 coming soon), Electric Spy, EV Log Book, PHEV support (coming soon) and analytics.",
     "Predictive maintenance, fuel intelligence, AI diagnostics, receipt & parts scanning, inventory, rego lookup, Rego Status (paid), resale estimates, Home Assistant integration (Phase 1 live), Electric Spy, EV Log Book, PHEV support (coming soon) and analytics — all deterministic-first."),
    # ---- ai-data.html meta ----
    ("ai-data.html",
     "What AutoBrain's AI does, exactly what data it sees for each feature, and how you stay in control. Never sold, never used to train models.",
     "What AutoBrain's AI does, exactly what data it sees for each feature, and how you stay in control. Every feature runs a deterministic rule-based path first — AI only enriches when reachable. Never sold, never used to train models."),
    ("ai-data.html",
     "How AutoBrain's AI Uses Your Data",
     "How AutoBrain's AI Uses Your Data — Deterministic-First"),
    ("ai-data.html",
     "What AutoBrain's AI does, exactly what data it sees for each feature, and how you stay in control.",
     "What AutoBrain's AI does, exactly what data it sees for each feature, and how you stay in control. Deterministic-first: every feature works even when the AI router is down."),
]

changed = []
for fname, old, new in edits:
    p = ROOT / fname
    s = p.read_text(encoding="utf-8")
    if old not in s:
        print(f"MISS {fname}: {old[:70]!r}")
        continue
    s = s.replace(old, new, 1)
    p.write_text(s, encoding="utf-8")
    changed.append(fname)

print("changed:", sorted(set(changed)))