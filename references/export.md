# Export phase

Package the manuscript. Produce Markdown always; EPUB + DOCX if pandoc is installed; PDF if a LaTeX engine is installed. **Never fail because a tool is missing** — produce what you can and print install hints.

## Before packaging

1. **Normalize chapter titles.** Each `chapters/ch_NN.md` should start with `# Chapter N: <Title>` (fiction) or `# <Chapter Title>` (nonfiction — chapter numbers optional). Pull titles from `outline.md`. Fix any inconsistencies.

2. **Rebuild `outline.md` from the actual chapters** — the outline may have drifted during drafting and revision. Run `scripts/assemble.py --rebuild-outline` to regenerate it from chapter headings and beats actually present. (Keep the original as `outline.foundation.md` for reference.)

3. **Rebuild `arc_summary.md`** — one-paragraph-per-chapter summary, used for marketing copy and the back matter. Run `scripts/assemble.py --arc-summary` (the script generates chapter skeletons; you flesh them out, or generate them in persona).

4. **Final slop sweep.** `python scripts/slop_scan.py chapters/*.md`. If the manuscript-level score is high, fix the worst offenders before export — slop compounds in a finished book.

5. **Foreshadowing/thread ledger resolved.** Confirm every entry is `resolved` or `red-herring`. Open threads at export = a structural defect.

6. **Canon / evidence current.** Fiction: `canon.md` up to date. Nonfiction: every claim sourced, **no `[NEEDS SOURCE]` tags remaining** (hard failure if any exist).

7. **No pending propagation debts.** All `state.json.debts` cleared.

## Assemble the manuscript

Run `python scripts/assemble.py`:

- Concatenates `chapters/ch_*.md` in numeric order → `manuscript.md`.
- Inserts a separator between chapters.
- Generates a table of contents from chapter headings.
- Reports per-chapter and total word counts to `results.tsv`.

Inspect `manuscript.md` — read the first and last chapter transitions to confirm continuity at the seams.

## Front matter

Build (or have the writer persona generate) into `front-matter.md`:

- **Title page** — title, author/pen name, (fiction) series info.
- **Copyright page** — placeholder; the user fills in real ISBN/copyright.
- **Dedication** (optional).
- **Epigraph** (optional; fiction).
- **Table of Contents** — from `assemble.py`.
- **Preface / Author's Note** (nonfiction) — why this book, who it's for.
- **Introduction** (nonfiction) — often counts as chapter 1 of the argument arc.

## Back matter

`back-matter.md`:

- **Acknowledgments** (optional).
- **Author's Note / Afterword** (fiction).
- **Sources / Bibliography** (nonfiction) — auto-built from `evidence.md`, deduplicated, sorted.
- **Appendices** (self-help: exercises, worksheets, "if this didn't work" guide; nonfiction: data tables, methodological notes).
- **Discussion questions** (optional; book clubs).
- **About the Author** + (if applicable) "Also by."
- **Call to action** — newsletter, next book, review request.

## Package formats

Run `python scripts/export.py <format>` (or `all`):

### Markdown (always)
Already produced by `assemble.py`. Output: `manuscript.md`. With front/back matter: `book.md` (front + manuscript + back concatenated).

### EPUB + DOCX (pandoc)
Requires `pandoc`. If missing, print:
```
ℹ pandoc not found — skipping EPUB/DOCX.
   Install:  brew install pandoc
   Then re-run: /skill book-forge export
```
Command (built by the script):
```
pandoc book.md -o "<title>.epub" --toc --metadata title="<title>" --metadata author="<author>"
pandoc book.md -o "<title>.docx" --toc --metadata title="<title>" --metadata author="<author>"
```
For nonfiction, pass `--bibliography=evidence.bib` if a BibTeX file exists (the script generates one from `evidence.md`).

### PDF (LaTeX)
Requires `tectonic` or `pdflatex`. If neither found, print:
```
ℹ LaTeX engine not found — skipping PDF.
   Install:  brew install --cask mactex     (full, ~4GB)
         or  cargo install tectonic          (lightweight)
   Then re-run: /skill book-forge export
```
The script uses a built-in LaTeX template (trade paperback, EB Garamond, like autonovel's typeset). For nonfiction, swap to a plainer academic template. Output: `<title>.pdf`.

## KDP readiness checklist (print to the user)

Before publishing:
- [ ] Word count in target range (novel: 60k–100k; nonfiction: 40k–80k; self-help: 30k–60k).
- [ ] EPUB validates (`epubcheck` if available — the script runs it and warns).
- [ ] PDF trim size correct (default 6×9in for fiction/nonfiction, 5.5×8.5in for self-help).
- [ ] Front matter complete (title, copyright, ToC).
- [ ] Back matter complete (about author, CTA).
- [ ] Nonfiction: every claim sourced in the bibliography.
- [ ] No `[NEEDS SOURCE]` tags anywhere.
- [ ] Foreshadowing/thread ledger fully resolved (fiction) / argument ledger fully synthesized (nonfiction).
- [ ] Manuscript slop score < 2.0.
- [ ] Final dual-persona review stopping condition met.

## KDP metadata (optional, generated on request)

If the user wants it, generate to `kdp-metadata.md`:
- **Blurb** (150–250 words; hook, stakes, voice; no spoilers).
- **7 keywords** (KDP keyword slots; mix broad and long-tail).
- **2 categories** (KDP BISAC categories).
- **Amazon description** (HTML-formatted version of the blurb with bold hooks).
- **Ad copy variants** (3 short, 3 long).

Generated by the writer persona from `arc_summary.md` + `voice.md`.

## Final state

- Set `state.json.phase: complete`.
- Commit everything: `git add -A && git commit -m "export: <title> (<formats>)"`.
- Tag the release: `git tag v1.0`.
- Print the deliverables list and the KDP checklist.

The book is done.
