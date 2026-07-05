#!/usr/bin/env python3
"""book-forge exporter.

Packages a finished manuscript into Markdown (always), EPUB + DOCX (via pandoc),
and PDF (via a LaTeX engine: tectonic or pdflatex).

NEVER FAILS because a tool is missing — produces what it can and prints install
hints for the rest.

Expects (built by assemble.py, or the skill itself):
  - manuscript.md         (assembled chapters)
  - front-matter.md       (optional; title, copyright, ToC, preface)
  - back-matter.md        (optional; ack, bibliography, appendices, about)

Reads book metadata from project.yaml / state.json if present.

Usage:
  python3 export.py                  # all formats
  python3 export.py markdown
  python3 export.py epub docx
  python3 export.py pdf
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys


# --------------------------------------------------------------------------- #
# Tool detection
# --------------------------------------------------------------------------- #

def which(tool: str) -> str | None:
    return shutil.which(tool)


def pandoc_available() -> bool:
    return which("pandoc") is not None


def latex_available() -> str | None:
    """Return the engine name if available, else None."""
    for engine in ("tectonic", "xelatex", "pdflatex", "lualatex"):
        if which(engine):
            return engine
    return None


# --------------------------------------------------------------------------- #
# Metadata
# --------------------------------------------------------------------------- #

def load_metadata() -> dict:
    """Pull title/author/author from project.yaml or state.json."""
    meta: dict[str, str | None] = {
        "title": None, "author": None, "lang": "en",
        "book_type": "fiction",
    }

    if os.path.isfile("project.yaml"):
        with open("project.yaml", "r", encoding="utf-8", errors="replace") as fh:
            blob = fh.read()
        for key in ("title", "subtitle", "author", "book_type"):
            m = re.search(rf"^{key}:\s*(\S.*?)\s*$", blob, re.MULTILINE)
            if m and m.group(1).lower() not in ("null", "none", "~"):
                meta[key] = m.group(1).strip().strip("'\"")
    elif os.path.isfile("state.json"):
        import json
        with open("state.json", "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for key in ("title", "book_type"):
            v = data.get(key)
            if v and str(v).lower() not in ("null", "none"):
                meta[key] = str(v)
        if "author" in data:
            meta["author"] = data["author"]

    # Fallback title
    if not meta["title"]:
        meta["title"] = "Untitled Manuscript"
    return meta


def slugify(text: str) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower())
    s = re.sub(r"[\s_-]+", "-", s).strip("-")
    return s or "book"


# --------------------------------------------------------------------------- #
# Build book.md (front + manuscript + back)
# --------------------------------------------------------------------------- #

def build_book_md(meta: dict) -> str:
    """Concatenate front-matter + manuscript + back-matter into book.md.
    Returns the path to book.md."""
    parts: list[str] = []

    # If no front-matter.md exists, generate a minimal one
    if os.path.isfile("front-matter.md"):
        with open("front-matter.md", "r", encoding="utf-8", errors="replace") as fh:
            parts.append(fh.read().rstrip())
    else:
        parts.append(f"% {meta['title']}")
        if meta.get("author"):
            parts.append(f"% {meta['author']}")
        parts.append("")

    if os.path.isfile("manuscript.md"):
        with open("manuscript.md", "r", encoding="utf-8", errors="replace") as fh:
            parts.append(fh.read().rstrip())
    else:
        print("export: manuscript.md not found. Run assemble.py first.", file=sys.stderr)
        sys.exit(2)

    if os.path.isfile("back-matter.md"):
        with open("back-matter.md", "r", encoding="utf-8", errors="replace") as fh:
            parts.append(fh.read().rstrip())

    out = "book.md"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n\n---\n\n".join(parts) + "\n")
    return out


# --------------------------------------------------------------------------- #
# Format producers
# --------------------------------------------------------------------------- #

def export_epub(book_md: str, meta: dict, out_dir: str) -> str | None:
    if not pandoc_available():
        print("  \u2139 pandoc not found \u2014 skipping EPUB/DOCX.")
        print("     Install:  brew install pandoc")
        return None
    title = meta["title"]
    out = os.path.join(out_dir, f"{slugify(title)}.epub")
    cmd = [
        "pandoc", book_md,
        "-o", out,
        "--toc", "--toc-depth=2",
        f"--metadata=title:{title}",
        f"--metadata=lang:{meta.get('lang', 'en')}",
    ]
    if meta.get("author"):
        cmd.append(f"--metadata=author:{meta['author']}")
    # Nonfiction: include bibliography if it exists
    bib = "evidence.bib" if os.path.isfile("evidence.bib") else None
    if bib:
        cmd += [f"--bibliography={bib}", "--citeproc"]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  \u2713 EPUB  {out}")
        return out
    except subprocess.CalledProcessError as e:
        print(f"  \u2717 EPUB failed: {e.stderr.strip()}", file=sys.stderr)
        return None


def export_docx(book_md: str, meta: dict, out_dir: str) -> str | None:
    if not pandoc_available():
        return None  # message printed by export_epub
    title = meta["title"]
    out = os.path.join(out_dir, f"{slugify(title)}.docx")
    cmd = [
        "pandoc", book_md,
        "-o", out,
        "--toc", "--toc-depth=2",
        f"--metadata=title:{title}",
    ]
    if meta.get("author"):
        cmd.append(f"--metadata=author:{meta['author']}")
    bib = "evidence.bib" if os.path.isfile("evidence.bib") else None
    if bib:
        cmd += [f"--bibliography={bib}", "--citeproc"]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  \u2713 DOCX  {out}")
        return out
    except subprocess.CalledProcessError as e:
        print(f"  \u2717 DOCX failed: {e.stderr.strip()}", file=sys.stderr)
        return None


# Minimal LaTeX book template (trade paperback)
LATEX_TEMPLATE = r"""\documentclass[10pt,twoside]{book}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{ebgaramond}
\usepackage[ebgaramond]{imbus}  % falls back gracefully
\usepackage[margin=1in,paperwidth=6in,paperheight=9in]{geometry}
\usepackage{microtype}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{lettrine}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\thepage}\fancyhead[RO]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\title{__TITLE__}
\author{__AUTHOR__}
\date{}
\begin{document}
\maketitle
\tableofcontents
\markboth{__TITLE__}{__TITLE__}
__BODY__
\end{document}
"""


def export_pdf(book_md: str, meta: dict, out_dir: str) -> str | None:
    engine = latex_available()
    if not engine:
        print("  \u2139 LaTeX engine not found \u2014 skipping PDF.")
        print("     Install:  brew install --cask mactex    (full, ~4GB)")
        print("            or  cargo install tectonic         (lightweight)")
        return None
    title = meta["title"]
    author = meta.get("author") or ""
    # Use pandoc to convert md -> tex body, then wrap.
    if not pandoc_available():
        print("  \u2717 PDF needs pandoc + LaTeX; pandoc missing.", file=sys.stderr)
        return None
    base = slugify(title)
    # Convert to standalone LaTeX via pandoc using our template
    template_path = os.path.join(out_dir, f"{base}.tex")
    tex_body_cmd = [
        "pandoc", book_md, "-t", "latex",
        "--variable=geometry:margin=1in",
    ]
    try:
        body = subprocess.run(tex_body_cmd, check=True, capture_output=True, text=True).stdout
    except subprocess.CalledProcessError as e:
        print(f"  \u2717 PDF md->tex failed: {e.stderr.strip()}", file=sys.stderr)
        return None

    tex = (LATEX_TEMPLATE
           .replace("__TITLE__", title.replace("&", r"\&"))
           .replace("__AUTHOR__", author.replace("&", r"\&"))
           .replace("__BODY__", body))
    with open(template_path, "w", encoding="utf-8") as fh:
        fh.write(tex)

    pdf_target = os.path.join(out_dir, f"{base}.pdf")
    try:
        if engine == "tectonic":
            subprocess.run(
                ["tectonic", "--outdir", out_dir, template_path],
                check=True, capture_output=True, text=True,
            )
        else:
            subprocess.run(
                [engine, "-interaction=nonstopmode",
                 f"-output-directory={out_dir}", template_path],
                check=True, capture_output=True, text=True,
            )
        if os.path.isfile(pdf_target):
            print(f"  \u2713 PDF   {pdf_target}")
            return pdf_target
        print(f"  \u2717 PDF build produced no output", file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        print(f"  \u2717 PDF build failed: {e.stderr.strip()[:300]}", file=sys.stderr)
        return None


def check_epub(epub_path: str | None) -> None:
    if not epub_path:
        return
    if not which("epubcheck"):
        print("  \u2139 epubcheck not found \u2014 skipping EPUB validation.")
        print("     Install:  brew install epubcheck")
        return
    try:
        r = subprocess.run(["epubcheck", epub_path],
                           capture_output=True, text=True)
        if r.returncode == 0:
            print(f"  \u2713 EPUB validates")
        else:
            print(f"  \u26a0 EPUB validation warnings/errors:")
            print("    " + r.stderr.strip().replace("\n", "\n    ")[:500])
    except FileNotFoundError:
        pass


# --------------------------------------------------------------------------- #
# KDP readiness checklist
# --------------------------------------------------------------------------- #

def kdp_checklist(meta: dict) -> None:
    print("\nKDP readiness checklist:")
    checks = [
        ("manuscript.md exists", os.path.isfile("manuscript.md")),
        ("state.json phase = export or complete", _phase_ready()),
        ("No [NEEDS SOURCE] tags in manuscript", _no_unsourced()),
        ("canon.md / evidence.md present", os.path.isfile("canon.md") or os.path.isfile("evidence.md")),
        ("outline.md present", os.path.isfile("outline.md")),
        ("front-matter.md present", os.path.isfile("front-matter.md")),
        ("back-matter.md present", os.path.isfile("back-matter.md")),
    ]
    for label, ok in checks:
        print(f"  [{'x' if ok else ' '}] {label}")
    print("\nWord count targets (verify):")
    print("  novel: 60k-100k | nonfiction: 40k-80k | self-help: 30k-60k")


def _phase_ready() -> bool:
    if not os.path.isfile("state.json"):
        return False
    import json
    try:
        with open("state.json") as fh:
            return json.load(fh).get("phase") in ("export", "complete")
    except Exception:
        return False


def _no_unsourced() -> bool:
    if not os.path.isfile("manuscript.md"):
        return True
    with open("manuscript.md", "r", encoding="utf-8", errors="replace") as fh:
        return "[NEEDS SOURCE]" not in fh.read()


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="book-forge exporter")
    p.add_argument("formats", nargs="*",
                   default=["all"],
                   help="formats to produce: markdown epub docx pdf all (default: all)")
    p.add_argument("--out-dir", default="exports", help="output directory (default: exports)")
    args = p.parse_args(argv)

    fmts = args.formats if args.formats else ["all"]
    if "all" in fmts:
        fmts = ["markdown", "epub", "docx", "pdf"]
    fmts_set = set(fmts)

    os.makedirs(args.out_dir, exist_ok=True)
    meta = load_metadata()
    print(f"Exporting: {meta['title']}"
          + (f" by {meta['author']}" if meta.get("author") else ""))
    print(f"Formats requested: {', '.join(sorted(fmts_set))}\n")

    # Markdown is always produced via book.md (front + manuscript + back)
    book_md = build_book_md(meta)
    if "markdown" in fmts_set:
        md_out = os.path.join(args.out_dir, "book.md")
        shutil.copyfile(book_md, md_out)
        print(f"  \u2713 MD    {md_out}")

    produced: list[str | None] = []
    if "epub" in fmts_set:
        epub = export_epub(book_md, meta, args.out_dir)
        produced.append(epub)
        if epub:
            check_epub(epub)
    if "docx" in fmts_set:
        produced.append(export_docx(book_md, meta, args.out_dir))
    if "pdf" in fmts_set:
        produced.append(export_pdf(book_md, meta, args.out_dir))

    kdp_checklist(meta)

    ok = [p for p in produced if p]
    print(f"\nProduced {len(ok)} packaged format(s).")
    if len(ok) < len(produced):
        print("Some formats skipped \u2014 see install hints above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
