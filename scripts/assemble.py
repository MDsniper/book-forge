#!/usr/bin/env python3
"""book-forge manuscript assembler.

Concatenates chapters/ in numeric order into manuscript.md, normalizes titles,
builds a table of contents, and reports word counts. Also supports rebuilding
outline.md and arc_summary.md skeletons from the actual chapters on disk.

Usage:
  python3 assemble.py                         # concatenate -> manuscript.md
  python3 assemble.py --rebuild-outline       # rewrite outline.md from chapter headings
  python3 assemble.py --arc-summary           # generate arc_summary.md skeleton
  python3 assemble.py --chapters-dir chapters --out manuscript.md
"""
from __future__ import annotations

import argparse
import os
import re
import sys

CHAPTER_RE = re.compile(r"ch_(\d+)\.md$", re.IGNORECASE)
HEADING_RE = re.compile(r"^#{1,3}\s+(.*)$", re.MULTILINE)
NUMBERED_HEADING_RE = re.compile(r"^chapter\s+\d+\b", re.IGNORECASE)


def _numbered_label(num: "int | None", heading: str) -> str:
    """Chapter label for listings — avoids doubling when heading already reads 'Chapter N: ...'."""
    if NUMBERED_HEADING_RE.match(heading):
        return heading
    return f"Chapter {num if num else '?'}: {heading}"


def natural_chapter_sort(path: str) -> tuple[int, str]:
    m = CHAPTER_RE.search(os.path.basename(path))
    return (int(m.group(1)) if m else 0, path)


def list_chapters(chapters_dir: str) -> list[str]:
    if not os.path.isdir(chapters_dir):
        return []
    files = [os.path.join(chapters_dir, f) for f in os.listdir(chapters_dir)
             if CHAPTER_RE.search(f)]
    return sorted(files, key=natural_chapter_sort)


def word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def first_heading(text: str) -> str | None:
    m = HEADING_RE.search(text)
    return m.group(1).strip() if m else None


def assemble(chapters: list[str], out_path: str, title: str | None) -> tuple[int, int]:
    """Returns (total_words, chapter_count)."""
    parts: list[str] = []
    toc: list[str] = []

    if title:
        parts.append(f"# {title}\n")
        parts.append("\n---\n")

    total_words = 0
    for path in chapters:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read().rstrip()
        heading = first_heading(text) or os.path.basename(path)
        wc = word_count(text)
        total_words += wc
        # Extract chapter number from filename for TOC ordering
        m = CHAPTER_RE.search(os.path.basename(path))
        num = int(m.group(1)) if m else None
        toc_entry = f"- {_numbered_label(num, heading)} ({wc:,} words)"
        toc.append(toc_entry)
        parts.append(text)
        parts.append("\n\n---\n")  # chapter separator

    # Build TOC at the top (after title)
    body_idx = 1 if title else 0
    toc_block = "## Table of Contents\n\n" + "\n".join(toc) + "\n\n---\n"
    parts.insert(body_idx, toc_block)

    out = "\n".join(parts).rstrip() + "\n"
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(out)
    return total_words, len(chapters)


def rebuild_outline(chapters: list[str], book_type: str, out_path: str) -> int:
    """Generate an outline.md skeleton from the chapters on disk. Returns chapter count."""
    lines = [
        "# Outline (rebuilt from chapters)",
        "",
        f"**Framework:** <auto-detected — confirm>",
        f"**Book type:** {book_type}",
        "",
        "## Part 1 — Beats",
        "",
    ]
    for path in chapters:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        heading = first_heading(text) or os.path.basename(path)
        wc = word_count(text)
        m = CHAPTER_RE.search(os.path.basename(path))
        num = int(m.group(1)) if m else None
        lines.append(f"### {_numbered_label(num, heading)}")
        lines.append(f"- Word count: {wc:,}")
        lines.append(f"- Beats: <fill in from the chapter>")
        lines.append("")
    lines += [
        "## Part 2 — Foreshadowing / argument ledger",
        "",
        "| ID | Planted (ch) | Payoff / Synthesis (ch) | Thread / Claim | Status |",
        "|----|--------------|--------------------------|----------------|--------|",
        "|    |              |                          |                | open   |",
        "",
    ]
    # Preserve the original outline if present
    if os.path.isfile(out_path):
        backup = out_path + ".bak"
        os.replace(out_path, backup)
        lines.append(f"(Original outline preserved at `{os.path.basename(backup)}`.)")
        lines.append("")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(chapters)


def arc_summary(chapters: list[str], out_path: str) -> int:
    """Generate arc_summary.md skeleton (one paragraph stub per chapter)."""
    lines = ["# Arc summary", ""]
    lines.append("_(One paragraph per chapter, for marketing and panel eval. Fill these in.)_")
    lines.append("")
    for path in chapters:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        heading = first_heading(text) or os.path.basename(path)
        wc = word_count(text)
        m = CHAPTER_RE.search(os.path.basename(path))
        num = int(m.group(1)) if m else None
        lines.append(f"## {_numbered_label(num, heading)} ({wc:,} words)")
        lines.append("")
        lines.append(f"<one-paragraph summary of what happens / what's argued in this chapter>")
        lines.append("")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return len(chapters)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="book-forge manuscript assembler")
    p.add_argument("--chapters-dir", default="chapters", help="chapter directory (default: chapters)")
    p.add_argument("--out", default="manuscript.md", help="output manuscript file")
    p.add_argument("--title", default=None, help="book title for the manuscript header")
    p.add_argument("--book-type", default="fiction",
                   choices=["fiction", "nonfiction", "self-help"],
                   help="book type, used by --rebuild-outline")
    p.add_argument("--rebuild-outline", action="store_true",
                   help="rewrite outline.md from the chapters on disk")
    p.add_argument("--arc-summary", action="store_true",
                   help="generate arc_summary.md skeleton")
    p.add_argument("--outline-out", default="outline.md")
    p.add_argument("--arc-out", default="arc_summary.md")
    args = p.parse_args(argv)

    chapters = list_chapters(args.chapters_dir)
    if not chapters:
        print(f"assemble: no chapters found in {args.chapters_dir}/", file=sys.stderr)
        return 2

    did_something = False
    if args.rebuild_outline:
        n = rebuild_outline(chapters, args.book_type, args.outline_out)
        print(f"assemble: rebuilt {args.outline_out} from {n} chapters "
              f"(original backed up if it existed).")
        did_something = True

    if args.arc_summary:
        n = arc_summary(chapters, args.arc_out)
        print(f"assemble: wrote {args.arc_out} skeleton ({n} chapters).")
        did_something = True

    if not did_something:
        # Default: assemble the manuscript
        title = args.title
        if title is None:
            # Try to read from project.yaml or state.json
            for cfg in ("project.yaml", "state.json"):
                if os.path.isfile(cfg):
                    with open(cfg, "r", encoding="utf-8", errors="replace") as fh:
                        blob = fh.read()
                    m = re.search(r"title:\s*(\S.*?)\s*$", blob, re.MULTILINE)
                    if not m:
                        m = re.search(r'"title"\s*:\s*"([^"]+)"', blob)
                    if m and m.group(1).lower() not in ("null", "none"):
                        title = m.group(1).strip().strip("'\"")
                        break
        total_wc, n = assemble(chapters, args.out, title)
        print(f"assemble: wrote {args.out} — {n} chapters, {total_wc:,} words total.")
        # Per-chapter breakdown
        for path in chapters:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
            wc = word_count(text)
            print(f"  {os.path.basename(path):<14}  {wc:>6,} words")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
