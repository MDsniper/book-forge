#!/usr/bin/env python3
"""book-forge structural beat calculator.

Given a chapter count and a framework, prints the exact chapter each structural
beat lands on. Used during foundation to validate the outline, and during
drafting to confirm beats are landing where they should.

Frameworks:
  fiction (default):   Save the Cat!-style commercial arc
  story-circle:        Dan Harmon's 8-step circle
  7-point:             Dan Wells' 7-point structure
  nonfiction:          argument arc (Setup -> Problem -> Framework ->
                       Evidence -> Application -> Synthesis)
  self-help:           same as nonfiction but with methods-chapter emphasis

Usage:
  python3 beat_math.py 22
  python3 beat_math.py 30 --mode nonfiction
  python3 beat_math.py 24 --mode story-circle
"""
from __future__ import annotations

import argparse
import math
import sys


def _clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, n))


def _round_up(frac: float, total: int) -> int:
    """Beat lands at fraction `frac` of total chapters, rounded up
    (better to enter a beat a touch late than early)."""
    return _clamp(math.ceil(frac * total), 1, total)


def _round(frac: float, total: int) -> int:
    return _clamp(round(frac * total), 1, total)


def beats_fiction(total: int) -> list[tuple[str, int]]:
    """Save the Cat! 15-beat mapping (compressed for novel chapter granularity)."""
    # Save the Cat! percentages are of the *whole* story
    b = [
        ("Opening Image",         _round(0.01, total)),
        ("Theme Stated",          _round(0.05, total)),
        ("Catalyst",              _round(0.10, total)),   # inciting incident
        ("Break into Two",        _round(0.20, total)),   # act 2 begins
        ("B Story",               _round(0.22, total)),
        ("Midpoint",              _round(0.50, total)),
        ("Bad Guys Close In",     _round(0.62, total)),
        ("All Is Lost",           _round(0.75, total)),   # twist / lowest point
        ("Dark Night of Soul",    _round(0.78, total)),
        ("Break into Three",      _round(0.80, total)),
        ("Finale (climax start)", _round(0.85, total)),
        ("Final Image",           total),
    ]
    return b


def beats_story_circle(total: int) -> list[tuple[str, int]]:
    """Dan Harmon's Story Circle, 8 steps mapped across chapters."""
    fracs = [0.05, 0.18, 0.30, 0.42, 0.55, 0.68, 0.82, 0.98]
    names = [
        "1. YOU (comfort)",
        "2. NEED",
        "3. GO (enter unfamiliar)",
        "4. SEARCH (adapt)",
        "5. FIND (get what they wanted)",
        "6. TAKE (pay the price)",
        "7. RETURN (to familiar, changed)",
        "8. CHANGE",
    ]
    return [(name, _clamp(round(f * total), 1, total)) for name, f in zip(names, fracs)]


def beats_seven_point(total: int) -> list[tuple[str, int]]:
    """Dan Wells' 7-Point Story Structure."""
    fracs = [0.05, 0.20, 0.35, 0.50, 0.65, 0.80, 0.97]
    names = [
        "Hook",
        "Plot Turn 1",
        "Pinch 1",
        "Midpoint",
        "Pinch 2",
        "Plot Turn 2",
        "Resolution",
    ]
    return [(name, _clamp(round(f * total), 1, total)) for name, f in zip(names, fracs)]


def beats_nonfiction(total: int) -> list[tuple[str, int]]:
    """Argument arc: Setup -> Problem -> Framework -> Evidence -> Application -> Synthesis."""
    b = [
        ("Setup (why this matters)",            _round_up(0.10, total)),
        ("Problem (current state)",             _round_up(0.20, total)),
        ("Framework (the lens)",                _round_up(0.35, total)),
        ("Evidence (the case)",                 _round_up(0.65, total)),
        ("Application (what to do)",            _round_up(0.85, total)),
        ("Synthesis (tying together + steelman)", total),
    ]
    return b


def beats_self_help(total: int) -> list[tuple[str, int]]:
    """Self-help arc: same as nonfiction but with a methods chapter called out."""
    base = beats_nonfiction(total)
    # Insert a "core method" beat at ~25% if there's room
    methods_ch = _round_up(0.25, total)
    # Don't duplicate an existing beat chapter; nudge if collision
    existing = {ch for _, ch in base}
    if methods_ch in existing:
        methods_ch = max(1, methods_ch - 1)
    base.insert(2, ("Core Method (the technique)", methods_ch))
    return base


def render(beats: list[tuple[str, int]], total: int, mode: str) -> str:
    lines = [f"Structural beats — mode={mode}, {total} chapters", "=" * 50]
    prev = 0
    for name, ch in beats:
        marker = ""
        if ch == prev:
            marker = "  ⚠ COLLISION with previous beat — merge or insert"
        gap = "" if prev == 0 else f"  (+{ch - prev} ch)"
        lines.append(f"  ch {ch:>3}  {name}{gap}{marker}")
        prev = ch
    lines.append("=" * 50)
    lines.append("Notes:")
    lines.append("  - If a beat lands between chapters, push it LATER (ceil), not earlier.")
    lines.append("  - COLLISION warnings mean two beats share a chapter — fix the outline.")
    lines.append("  - For a series, leave series-arc threads open at the Final Image/Synthesis.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="book-forge structural beat calculator")
    p.add_argument("chapters", type=int, help="total chapter count")
    p.add_argument("--mode", default="fiction",
                   choices=["fiction", "save-the-cat", "story-circle", "7-point",
                            "nonfiction", "self-help"],
                   help="framework (default: fiction / save-the-cat)")
    args = p.parse_args(argv)

    if args.chapters < 1:
        print("chapters must be >= 1", file=sys.stderr)
        return 2

    mode = "fiction" if args.mode == "save-the-cat" else args.mode
    table = {
        "fiction": beats_fiction,
        "story-circle": beats_story_circle,
        "7-point": beats_seven_point,
        "nonfiction": beats_nonfiction,
        "self-help": beats_self_help,
    }[mode]

    beats = table(args.chapters)
    print(render(beats, args.chapters, mode))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
