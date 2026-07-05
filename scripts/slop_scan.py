#!/usr/bin/env python3
"""book-forge mechanical slop scanner.

Detects AI-tell patterns in prose using regex only (no LLM). Returns a 0-10
penalty intended to be subtracted from the LLM judge's overall score.

Reads lexicons from:
  - <skill_dir>/assets/banned-words.txt   (Tier 1 single words / Tier 3 phrases)
  - <skill_dir>/assets/ai-tells.txt        (compiled regex patterns)
  - <book_dir>/.book-forge/banned-words.txt  (project overrides, optional)
  - <book_dir>/.book-forge/ai-tells.txt       (project overrides, optional)

The skill dir is auto-located (parent of this script's dir). Book dir is the
current working directory by default (override with --book-dir).

Checks:
  - Tier 1 banned-word hits (case-insensitive, whole-word)
  - Tier 3 banned-phrase hits (case-insensitive substring)
  - Cluster detection (>=3 Tier-1 hits per 500 words -> penalty escalates)
  - AI-tell regex matches
  - Em-dash density (>15 / 1000 words -> penalty)
  - Sentence-length coefficient of variation (<0.3 -> penalty)
  - Transition-opener ratio (>0.3 of paragraphs -> penalty)
  - Show-don't-tell patterns ("felt X", "was Y", "knew that")

Usage:
  python3 slop_scan.py chapters/ch_01.md
  python3 slop_scan.py chapters/*.md
  python3 slop_scan.py manuscript.md --json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)  # .../book-forge/
ASSET_BANNED = os.path.join(SKILL_DIR, "assets", "banned-words.txt")
ASSET_TELLS = os.path.join(SKILL_DIR, "assets", "ai-tells.txt")

# Transition openers (paragraph-leading words that flag mechanical structure)
TRANSITION_OPENERS = re.compile(
    r"^\s*(however|moreover|meanwhile|suddenly|furthermore|additionally|"
    r"consequently|nevertheless|nonetheless|therefore|thus|hence|"
    r"ultimately|finally|subsequently|shortly|shortly after|"
    r"instantly|immediately|shortly thereafter|"
    r"as (?:she|he|they|it) (?:walked|turned|looked|sat|stood|moved))\b",
    re.IGNORECASE,
)

# Show-don't-tell patterns
SHOW_DONT_TELL = [
    re.compile(r"\b(?:he|she|they|it|i|we) felt\b", re.IGNORECASE),
    re.compile(r"\b(?:he|she|they) was (?:angry|sad|happy|afraid|scared|tired|relieved|confused|surprised|excited|disgusted)\b", re.IGNORECASE),
    re.compile(r"\b(?:he|she|they) knew that\b", re.IGNORECASE),
    re.compile(r"\b(?:he|she|they) saw that\b", re.IGNORECASE),
    re.compile(r"\b(?:he|she|they) realized that\b", re.IGNORECASE),
]


# --------------------------------------------------------------------------- #
# Lexicon loading
# --------------------------------------------------------------------------- #

def _iter_lines(path: str):
    """Yield non-comment, non-blank lines from a file. Returns [] if missing."""
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            yield line


def load_banned_words(asset_path: str, project_path: str | None) -> tuple[list[str], list[str]]:
    """Return (tier1_words, tier3_phrases).

    Heuristic: a lexicon entry with a space is a phrase (Tier 3); else a word (Tier 1).
    """
    words: set[str] = set()
    phrases: set[str] = set()
    for path in (asset_path, project_path):
        if not path:
            continue
        for entry in _iter_lines(path):
            if " " in entry:
                phrases.add(entry.lower())
            else:
                words.add(entry.lower())
    return sorted(words), sorted(phrases)


def load_ai_tells(asset_path: str, project_path: str | None) -> list[re.Pattern]:
    patterns: list[re.Pattern] = []
    for path in (asset_path, project_path):
        if not path:
            continue
        for line in _iter_lines(path):
            try:
                patterns.append(re.compile(line, re.IGNORECASE))
            except re.error:
                # Skip unparseable lines rather than failing the whole scan.
                continue
    return patterns


# --------------------------------------------------------------------------- #
# Text utilities
# --------------------------------------------------------------------------- #

def split_sentences(text: str) -> list[str]:
    """Crude sentence splitter. Good enough for length-stats."""
    # Strip markdown headings, blockquotes
    clean = re.sub(r"^#{1,6}\s+.*$", "", text, flags=re.MULTILINE)
    clean = re.sub(r"^>.*$", "", clean, flags=re.MULTILINE)
    parts = re.split(r"(?<=[.!?])\s+", clean)
    return [p.strip() for p in parts if p.strip()]


def split_paragraphs(text: str) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return [p for p in paras if p]


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def coefficient_of_variation(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance) / mean


# --------------------------------------------------------------------------- #
# Scan
# --------------------------------------------------------------------------- #

@dataclass
class ScanResult:
    file: str
    word_count: int = 0
    penalty: float = 0.0
    tier1_hits: list[tuple[str, int]] = field(default_factory=list)   # (word, count)
    tier3_hits: list[tuple[str, int]] = field(default_factory=list)
    tell_hits: list[tuple[str, int]] = field(default_factory=list)    # (pattern, count)
    clusters: int = 0
    em_dash_density: float = 0.0          # per 1000 words
    sentence_cv: float = 0.0
    transition_ratio: float = 0.0
    show_dont_tell_hits: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "word_count": self.word_count,
            "penalty": round(self.penalty, 2),
            "tier1_hits": self.tier1_hits,
            "tier3_hits": self.tier3_hits,
            "tell_hits": self.tell_hits,
            "clusters": self.clusters,
            "em_dash_density": round(self.em_dash_density, 2),
            "sentence_cv": round(self.sentence_cv, 3),
            "transition_ratio": round(self.transition_ratio, 3),
            "show_dont_tell_hits": self.show_dont_tell_hits,
            "notes": self.notes,
        }


def scan_text(text: str, path: str, tier1: list[str], tier3: list[str],
              tells: list[re.Pattern]) -> ScanResult:
    res = ScanResult(file=path)
    wc = word_count(text)
    res.word_count = wc
    if wc == 0:
        res.notes.append("empty file")
        return res

    lower = text.lower()

    # Tier 1: whole-word banned words
    for w in tier1:
        # Use a word boundary; handle hyphens inside the term
        pattern = re.compile(r"\b" + re.escape(w) + r"\b", re.IGNORECASE)
        n = len(pattern.findall(text))
        if n:
            res.tier1_hits.append((w, n))

    # Tier 3: phrase substring
    for p in tier3:
        if p in lower:
            n = lower.count(p)
            res.tier3_hits.append((p, n))

    # AI-tell regex
    for pat in tells:
        n = len(pat.findall(text))
        if n:
            res.tell_hits.append((pat.pattern, n))

    # Cluster detection: Tier-1 density per 500 words
    tier1_total = sum(n for _, n in res.tier1_hits)
    if wc >= 200:  # only meaningful on real chunks
        per_500 = (tier1_total / wc) * 500
        if per_500 >= 3:
            res.clusters = int(per_500 // 3)
            res.notes.append(f"cluster: {tier1_total} Tier-1 words = {per_500:.1f}/500w")

    # Em-dash density (— and --)
    em_dashes = text.count("—") + len(re.findall(r"(?<!-)--(?!-)", text))
    res.em_dash_density = (em_dashes / wc) * 1000

    # Sentence-length CV
    sentences = split_sentences(text)
    if sentences:
        lengths = [float(word_count(s)) for s in sentences if word_count(s) > 0]
        res.sentence_cv = coefficient_of_variation(lengths)

    # Transition-opener ratio
    paras = split_paragraphs(text)
    if paras:
        opened = sum(1 for p in paras if TRANSITION_OPENERS.match(p))
        res.transition_ratio = opened / len(paras)

    # Show-don't-tell
    sdt = 0
    for pat in SHOW_DONT_TELL:
        sdt += len(pat.findall(text))
    res.show_dont_tell_hits = sdt

    # ---- Penalty calculation (0-10) ----
    penalty = 0.0

    # Tier 1: 0.4 each, clusters add 0.3 each
    penalty += min(tier1_total * 0.4, 3.0)
    penalty += min(res.clusters * 0.3, 1.5)

    # Tier 3 phrases: 0.5 each (capped)
    t3_total = sum(n for _, n in res.tier3_hits)
    penalty += min(t3_total * 0.5, 2.0)

    # AI tells: 0.6 each (capped)
    tell_total = sum(n for _, n in res.tell_hits)
    penalty += min(tell_total * 0.6, 3.0)

    # Em-dash density over 15/1000w: scale up
    if res.em_dash_density > 15:
        penalty += min((res.em_dash_density - 15) / 10.0, 1.5)

    # Sentence CV under 0.3: uniform length
    if 0 < res.sentence_cv < 0.3:
        penalty += (0.3 - res.sentence_cv) * 5.0  # max ~1.5

    # Transition-opener ratio over 0.3
    if res.transition_ratio > 0.3:
        penalty += min((res.transition_ratio - 0.3) * 5.0, 1.0)

    # Show-don't-tell density
    if wc > 0:
        sdt_per_1000 = (sdt / wc) * 1000
        if sdt_per_1000 > 5:
            penalty += min((sdt_per_1000 - 5) / 10.0, 1.0)

    res.penalty = min(round(penalty, 2), 10.0)
    return res


def scan_file(path: str, tier1: list[str], tier3: list[str],
              tells: list[re.Pattern]) -> ScanResult:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    return scan_text(text, path, tier1, tier3, tells)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="book-forge mechanical slop scanner")
    p.add_argument("files", nargs="+", help="markdown/text files to scan")
    p.add_argument("--book-dir", default=os.getcwd(),
                   help="book directory for project overrides (default: cwd)")
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    p.add_argument("--threshold", type=float, default=4.0,
                   help="exit nonzero if total penalty exceeds this (default 4.0)")
    args = p.parse_args(argv)

    proj_banned = os.path.join(args.book_dir, ".book-forge", "banned-words.txt")
    proj_tells = os.path.join(args.book_dir, ".book-forge", "ai-tells.txt")

    tier1, tier3 = load_banned_words(
        ASSET_BANNED,
        proj_banned if os.path.isfile(proj_banned) else None,
    )
    tells = load_ai_tells(
        ASSET_TELLS,
        proj_tells if os.path.isfile(proj_tells) else None,
    )

    results: list[ScanResult] = []
    for f in args.files:
        if not os.path.isfile(f):
            print(f"slop_scan: skip missing file {f}", file=sys.stderr)
            continue
        results.append(scan_file(f, tier1, tier3, tells))

    if not results:
        print("slop_scan: no files scanned", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        total_penalty = 0.0
        for r in results:
            total_penalty += r.penalty
            print(f"\n=== {r.file} ===")
            print(f"  words:          {r.word_count}")
            print(f"  penalty:        {r.penalty:.2f} / 10")
            print(f"  em-dash/1000w:  {r.em_dash_density:.2f}  (flag if >15)")
            print(f"  sentence CV:    {r.sentence_cv:.3f}    (flag if <0.3)")
            print(f"  transition %:   {r.transition_ratio*100:.1f}%  (flag if >30%)")
            print(f"  show/tell hits: {r.show_dont_tell_hits}")
            if r.tier1_hits:
                top = sorted(r.tier1_hits, key=lambda x: -x[1])[:10]
                print(f"  Tier-1 banned:  {top}")
            if r.tier3_hits:
                print(f"  Tier-3 phrases: {r.tier3_hits[:10]}")
            if r.tell_hits:
                print(f"  AI-tell regex:  {r.tell_hits[:10]}")
            if r.notes:
                print(f"  notes:          {r.notes}")
        if len(results) > 1:
            avg = total_penalty / len(results)
            print(f"\n=== SUMMARY: {len(results)} files, avg penalty {avg:.2f}, total {total_penalty:.2f} ===")

    # Exit nonzero only if a single file is over threshold (multi-file = report mode)
    worst = max(r.penalty for r in results)
    return 0 if worst <= args.threshold or len(results) > 1 else 1


if __name__ == "__main__":
    raise SystemExit(main())
