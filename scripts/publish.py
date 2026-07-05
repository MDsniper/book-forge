#!/usr/bin/env python3
"""book-forge publish helper.

Deterministic (non-LLM) helper for the publish phase. Generates the real,
sellable-book artifacts: copyright page, cover spec sheet, pricing math,
KDP/Ingram metadata templates, legal disclaimer selection, KDP readiness
checklist, and step-by-step instructions.

Usage:
  python3 publish.py copyright                  # generate copyright-page.md
  python3 publish.py cover-spec                 # generate cover-spec.txt
  python3 publish.py pricing                    # generate pricing.md
  python3 publish.py metadata                   # scaffold kdp/ingram templates
  python3 publish.py disclaimers                # select + emit disclaimers
  python3 publish.py checklist                  # KDP readiness report
  python3 publish.py validate-targets           # check word count vs genre
  python3 publish.py all                        # everything, in order
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime

# --------------------------------------------------------------------------- #
# Metadata loading
# --------------------------------------------------------------------------- #

def _yaml_scalar(raw: str) -> str:
    """Extract a YAML scalar, stripping a trailing unquoted '#' comment."""
    raw = raw.strip()
    if raw[:1] in ("'", '"'):
        quote = raw[0]
        end = raw.find(quote, 1)
        return raw[1:end] if end != -1 else raw[1:]
    idx = raw.find(" #")
    if idx != -1:
        raw = raw[:idx]
    elif raw.startswith("#"):
        raw = ""
    return raw.strip()


def load_meta() -> dict:
    meta = {
        "title": "Untitled", "subtitle": "", "author": "Author",
        "book_type": "fiction", "genre": "", "subgenre": "",
        "series": "", "series_position": "",
        "imprint": "", "city": "", "url": "",
        "year": str(datetime.now().year),
        "edition": "First Edition",
        "isbn_print": "", "isbn_ebook": "", "lccn": "",
        "cover_designer": "", "editor": "",
        "trim": "6x9", "paper": "cream",
    }
    if os.path.isfile("project.yaml"):
        with open("project.yaml", "r", encoding="utf-8", errors="replace") as fh:
            blob = fh.read()
        for key in list(meta.keys()):
            m = re.search(rf"^{key}:\s*(\S.*?)\s*$", blob, re.MULTILINE)
            if m:
                val = _yaml_scalar(m.group(1))
                if val.lower() not in ("null", "none", "~", ""):
                    meta[key] = val
    if os.path.isfile("state.json"):
        try:
            with open("state.json", "r", encoding="utf-8") as fh:
                data = json.load(fh)
            for key in ("title", "book_type", "genre"):
                v = data.get(key)
                if v and str(v).lower() not in ("null", "none"):
                    meta[key] = str(v)
        except Exception:
            pass
    return meta


def page_count(manuscript_md: str = "manuscript.md") -> int:
    if not os.path.isfile(manuscript_md):
        return 0
    with open(manuscript_md, "r", encoding="utf-8", errors="replace") as fh:
        wc = len(re.findall(r"\b[\w']+\b", fh.read()))
    return max(1, wc // 250)


DISCLAIMERS = {
    "fiction": (
        'This is a work of fiction. Names, characters, places, and\n'
        'incidents either are the product of the author\'s imagination\n'
        'or are used fictitiously. Any resemblance to actual persons,\n'
        'living or dead, events, or locales is entirely coincidental.'
    ),
    "self-help": (
        'The information in this book is provided for educational and\n'
        'informational purposes only and is not a substitute for\n'
        'professional medical, psychological, legal, or financial\n'
        'advice. The author and publisher disclaim any liability\n'
        'arising from the use or misuse of the methods described\n'
        'herein. Consult a qualified professional before making\n'
        'changes to your health, finances, or routines.'
    ),
    "nonfiction": (
        'The author and publisher have made every effort to ensure the\n'
        'accuracy of the information in this book at the time of\n'
        'publication. However, the information is provided without\n'
        'warranty of any kind. The author and publisher disclaim any\n'
        'liability arising from the use or misuse of the information\n'
        'contained herein.'
    ),
    "memoir": (
        'This memoir is based on the author\'s recollections. Some\n'
        'names, identifying details, and timelines have been changed\n'
        'to protect the privacy of others. The events are recounted\n'
        'to the best of the author\'s memory.\n\n'
        'NOTE: Memoir carries the highest defamation/privacy risk.\n'
        'Changing names is not enough if a real person is still\n'
        'identifiable. Obtain releases for anyone portrayed negatively\n'
        'or consult a publishing attorney before publication.'
    ),
}


def cmd_copyright(meta, out_dir):
    bt = meta.get("book_type", "fiction")
    disclaimer = DISCLAIMERS.get(bt, DISCLAIMERS["fiction"])
    lines = [meta["title"].upper()]
    if meta.get("subtitle"):
        lines.append(meta["subtitle"])
    if meta.get("series"):
        pos = f"Book {meta['series_position']}" if meta.get("series_position") else ""
        lines.append(f"{meta['series']}{', ' + pos if pos else ''}")
    lines += [
        "",
        f"Copyright © {meta['year']} by {meta['author']}",
        ("All rights reserved. No part of this book may be reproduced\n"
         "or transmitted in any form or by any means, electronic or\n"
         "mechanical, including photocopying, recording, or by any\n"
         "information storage and retrieval system, without permission\n"
         "in writing from the publisher, except by a reviewer who may\n"
         "quote brief passages in a review."),
        "",
        disclaimer,
        "",
    ]
    if meta.get("isbn_print"):
        lines.append(f"ISBN {meta['isbn_print']} (paperback)")
    if meta.get("isbn_ebook"):
        lines.append(f"ISBN {meta['isbn_ebook']} (ebook)")
    if not meta.get("isbn_print") and not meta.get("isbn_ebook"):
        lines.append("ISBN <assign from Bowker/Nielsen — see instructions.md>")
    if meta.get("lccn"):
        lines.append(f"Library of Congress Control Number: {meta['lccn']}")
    lines.append("")
    pub = meta.get("imprint") or f"Published by {meta['author']}"
    lines.append(f"{pub}" + (f", {meta['city']}" if meta.get("city") else ""))
    if meta.get("url"):
        lines.append(meta["url"])
    lines.append("")
    if meta.get("cover_designer"):
        lines.append(f"Cover design by {meta['cover_designer']}")
    if meta.get("editor"):
        lines.append(f"Edited by {meta['editor']}")
    lines += ["", f"{meta['edition']}: {meta['year']}",
              "10 9 8 7 6 5 4 3 2 1", "Printed in the United States of America"]

    out = os.path.join(out_dir, "copyright-page.md")
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# Copyright Page\n\n```\n" + "\n".join(lines) + "\n```\n")
    return out


def cmd_cover_spec(meta, out_dir):
    trim = meta.get("trim", "6x9")
    paper = meta.get("paper", "cream")
    pages = page_count()
    try:
        w, h = trim.lower().split("x")
        w_in, h_in = float(w), float(h)
    except Exception:
        w_in, h_in = 6.0, 9.0
    thickness = 0.002252 if paper == "white" else 0.0025
    spine = pages * thickness
    bleed = 0.125
    cover_w = w_in + spine + w_in + bleed * 3
    cover_h = h_in + bleed * 2
    lines = [
        "# Cover specification", "",
        f"Trim: {trim}  |  Paper: {paper}  |  Estimated pages: {pages}",
        f"Spine width: {spine:.3f}\" ({pages} × {thickness}\"/page)", "",
        "## Ebook cover (KDP / Apple / Kobo)",
        "  Dimensions: 1600 × 2560 px (ratio 1.6:1)",
        "  Min: 625 × 1000 px.  Max file: 5 MB.  300 DPI.  JPEG or TIFF.", "",
        "## Print cover (KDP paperback / IngramSpark)",
        f"  Total width : {cover_w:.3f}\"  (back {w_in}\" + spine {spine:.3f}\" + front {w_in}\" + bleed {bleed*3:.3f}\")",
        f"  Total height: {cover_h:.3f}\"  (trim {h_in}\" + bleed {bleed*2:.3f}\")",
        f"  Spine text viable: {'YES' if pages >= 100 else 'NO (need >=100 pages)'}",
        "  Format: full-bleed PDF, 300 DPI, embedded fonts.", "",
        "## Print interior",
        f"  Trim: {trim}.  Margins: MIRRORED, gutter > outer.  Embed all fonts.",
        "  Min 24 pages, max ~828 pages.", "",
        "## Cover design resources",
        "  Reedsy marketplace: $625-$1,250 typical",
        "  99designs contests: $299-$1,199",
        "  Damonza / Deranged Doctor Design: $500-$2,000",
        "  DIY: Canva, BookBrush, Reedsy Book Editor", "",
        "## Cover design rules (genre signals at thumbnail size)",
        "  - Title readable at 80-120px wide (Amazon thumbnail).",
        "  - One focal image, no clutter.",
        "  - Title >= 1/3 of cover height.",
        "  - Genre-coded typography.",
    ]
    out = os.path.join(out_dir, "cover-spec.txt")
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return out


def cmd_pricing(meta, out_dir):
    bt = meta.get("book_type", "fiction")
    pages = page_count()
    print_cost = 0.85 + 0.012 * pages if pages else 0
    rows = []
    for ebook_price in (2.99, 4.99, 7.99, 9.99, 12.99, 14.99):
        if 2.99 <= ebook_price <= 9.99:
            royalty_pct, delivery = 0.70, 0.06
        else:
            royalty_pct, delivery = 0.35, 0
        royalty = round(ebook_price * royalty_pct - delivery, 2)
        rows.append(f"  ${ebook_price:>5.2f} ebook  ->  {int(royalty_pct*100)}% royalty, ~${royalty:.2f}/sale")
    for print_price in (9.99, 12.99, 14.99, 16.99):
        royalty = round(print_price * 0.60 - print_cost, 2)
        rows.append(f"  ${print_price:>5.2f} print  ->  60% - ${print_cost:.2f} print = ~${royalty:.2f}/sale")
    rec_map = {
        "fiction": "Fiction ebook: $4.99-$7.99 (70% bracket). Print: $12.99-$14.99.",
        "nonfiction": "Nonfiction ebook: $9.99-$14.99 (often >$9.99 accepting 35%). Print: $14.99-$19.99.",
        "self-help": "Self-help ebook: $9.99-$14.99. Print: $14.99-$24.99. Readers pay for value/outcome.",
    }
    rec = rec_map.get(bt, rec_map["fiction"])
    out = os.path.join(out_dir, "pricing.md")
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# Pricing recommendation\n\n")
        fh.write(f"Book type: {bt}  |  Est. pages: {pages}  |  Est. print cost: ${print_cost:.2f}\n\n")
        fh.write("## Royalty math at candidate prices\n\n```\n")
        fh.write("\n".join(rows) + "\n```\n\n")
        fh.write(f"## Recommendation\n\n{rec}\n\n## Key constraints\n\n")
        fh.write("- KDP 70% royalty bracket: prices **$2.99-$9.99** only.\n")
        fh.write("- Below $2.99 or above $9.99 -> forced to 35%.\n")
        fh.write("- Print royalty = (60% × list) − print cost.\n")
        fh.write("- **Series-entry strategy**: Book 1 at $0.99 to funnel into Books 2-N.\n")
    return out


def cmd_metadata(meta, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    template = f"""# KDP metadata — {meta['title']}

(Writer persona fills in the [BRACKETS] from arc_summary.md + voice.md.)

## Required fields

- **Title**: {meta['title']}
- **Subtitle**: {meta.get('subtitle', '[for nonfiction SEO]')}
- **Author**: {meta['author']}
- **Series**: {meta.get('series', '[if part of a series]')}  |  **Volume**: {meta.get('series_position', '')}

## Description (HTML-formatted, max 4000 chars; sweet spot ~1800-2200)

```html
<b>[Hook — one explosive sentence]</b>
<h3>[Setup]</h3>
[Body — stakes, conflict, what makes this different. No spoilers.]
<h3>Perfect for readers of:</h3>
<ul><li>[comp title 1]</li><li>[comp title 2]</li></ul>
```

## 7 keywords (<=50 chars each; long-tail phrases beat single words)
1. [keyword 1]
2. [keyword 2]
3. [keyword 3]
4. [keyword 4]
5. [keyword 5]
6. [keyword 6]
7. [keyword 7]

## 2-10 BISAC categories (low-competition subcategories)
1. [category path]
2. [category path]

## Comp titles (for positioning, ad targeting, newsletter pitches)
1. [comp 1 — recent, same subgenre, similar audience]
2. [comp 2]
"""
    out = os.path.join(out_dir, "kdp-metadata.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(template)
    ingram = template.replace("KDP metadata", "IngramSpark metadata") + """
## IngramSpark-specific
- **Returns policy**: choose returnable. Options: return-and-ship OR destroy-in-place.
- **Global Distribution Fee**: 1.875% of wholesale (2026).
- **Use the SAME ISBN** as the KDP edition (must be self-owned).
"""
    out2 = os.path.join(out_dir, "ingram-metadata.md")
    with open(out2, "w", encoding="utf-8") as fh:
        fh.write(ingram)
    return out


def cmd_disclaimers(meta, out_dir):
    bt = meta.get("book_type", "fiction")
    selected = DISCLAIMERS.get(bt, DISCLAIMERS["fiction"])
    risks = []
    if os.path.isfile("manuscript.md"):
        with open("manuscript.md", "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if re.search(r"[♪♫]|lyrics:", text):
            risks.append("POSSIBLE SONG LYRICS — quoting copyrighted lyrics requires permission "
                         "from the song's music publisher (NOT Harry Fox — that's for cover recordings). "
                         "Workaround: refer to songs by title only.")
        if bt == "memoir":
            risks.append("MEMOIR DEFAMATION RISK — name changes aren't enough if a real person is "
                         "identifiable. Get releases for anyone portrayed negatively.")
        if bt == "self-help":
            if re.search(r"\b(cure|cures|heals|guaranteed|100%|always|never)\b", text, re.IGNORECASE):
                risks.append("SELF-HELP OVERCLAIMING — detected absolute/medical language. Soften to "
                             "'may help with', 'for many people', 'in most cases'.")
    out = os.path.join(out_dir, "legal-disclaimers.md")
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# Legal disclaimers + risk report\n\n")
        fh.write(f"Selected disclaimer for book_type={bt}:\n\n```\n{selected}\n```\n\n## Risk lint\n\n")
        if risks:
            for r in risks:
                fh.write(f"- ⚠ {r}\n")
        else:
            fh.write("- No high-risk patterns detected.\n")
    return out


def _phase_at_least(min_phase):
    order = ["seed", "foundation", "drafting", "revision", "export", "publish", "complete"]
    if not os.path.isfile("state.json"):
        return False
    try:
        with open("state.json") as fh:
            phase = json.load(fh).get("phase", "")
        return phase in order and order.index(phase) >= order.index(min_phase)
    except Exception:
        return False


def _no_unsourced():
    if not os.path.isfile("manuscript.md"):
        return True
    with open("manuscript.md", "r", encoding="utf-8", errors="replace") as fh:
        return "[NEEDS SOURCE]" not in fh.read()


def cmd_checklist(meta, out_dir):
    checks = [
        ("manuscript.md exists", os.path.isfile("manuscript.md")),
        ("state.json phase >= export", _phase_at_least("export")),
        ("No [NEEDS SOURCE] tags", _no_unsourced()),
        ("copyright-page.md generated", os.path.isfile(os.path.join(out_dir, "copyright-page.md"))),
        ("cover-spec.txt generated", os.path.isfile(os.path.join(out_dir, "cover-spec.txt"))),
        ("pricing.md generated", os.path.isfile(os.path.join(out_dir, "pricing.md"))),
        ("KDP metadata scaffolded", os.path.isfile(os.path.join(out_dir, "kdp-metadata.md"))),
        ("legal disclaimers selected", os.path.isfile(os.path.join(out_dir, "legal-disclaimers.md"))),
        ("front-matter.md present", os.path.isfile("front-matter.md")),
        ("back-matter.md present", os.path.isfile("back-matter.md")),
        ("ISBN assigned", bool(meta.get("isbn_print") or meta.get("isbn_ebook"))),
    ]
    out = os.path.join(out_dir, "checklist.md")
    os.makedirs(out_dir, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# KDP readiness checklist\n\n")
        for label, ok in checks:
            fh.write(f"- [{'x' if ok else ' '}] {label}\n")
        fh.write("\n## Manual steps (the human does these)\n\n")
        fh.write("- [ ] Buy ISBN(s) from Bowker (US) / Nielsen (UK) / Library and Archives (CA free)\n")
        fh.write("- [ ] Assign ISBNs in your Bowker dashboard (one per format)\n")
        fh.write("- [ ] (Optional) File US copyright at copyright.gov ($45)\n")
        fh.write("- [ ] Commission or design the cover per cover-spec.txt\n")
        fh.write("- [ ] Run epubcheck on the EPUB (brew install epubcheck)\n")
        fh.write("- [ ] Upload to KDP (ebook + print)\n")
        fh.write("- [ ] (Optional) Upload print to IngramSpark with own ISBN, returnable\n")
        fh.write("- [ ] (Optional) Produce audiobook via ACX\n")
        fh.write("- [ ] Launch: ARC team 2-4 weeks pre, newsletter + social on launch day\n")
    return out


def cmd_validate_targets(meta):
    NORMS = {
        "middle grade": (25000, 55000), "ya contemporary": (65000, 90000),
        "ya sff": (80000, 100000), "romance": (70000, 100000),
        "romantasy": (90000, 120000), "thriller": (80000, 100000),
        "mystery": (80000, 100000), "horror": (80000, 100000),
        "epic fantasy": (100000, 130000), "science fiction": (90000, 120000),
        "literary fiction": (70000, 100000), "memoir": (60000, 90000),
        "self-help": (35000, 60000), "narrative nonfiction": (70000, 100000),
        "novella": (15000, 40000),
    }
    total = 0
    if os.path.isfile("state.json"):
        try:
            with open("state.json") as fh:
                s = json.load(fh)
            total = s.get("total_words_target") or s.get("chapters_total", 0) * s.get("words_per_chapter", 0)
        except Exception:
            pass
    genre = (meta.get("genre") or "").lower()
    match = next(((k, lo, hi) for k, (lo, hi) in NORMS.items() if k in genre), None)
    if not match:
        return f"  genre '{genre}' not in norms table — skipping validation"
    k, lo, hi = match
    if total == 0:
        return f"  genre={k} norm={lo:,}-{hi:,} words (no target set)"
    if total < lo:
        return f"  ⚠ genre={k}: target {total:,} words BELOW norm {lo:,}-{hi:,}"
    if total > hi:
        return f"  ⚠ genre={k}: target {total:,} words ABOVE norm {lo:,}-{hi:,}"
    return f"  ✓ genre={k}: target {total:,} words within norm {lo:,}-{hi:,}"


def main(argv=None):
    p = argparse.ArgumentParser(description="book-forge publish helper")
    p.add_argument("command", choices=[
        "copyright", "cover-spec", "pricing", "metadata",
        "disclaimers", "checklist", "validate-targets", "all",
    ])
    p.add_argument("--out-dir", default="publish")
    args = p.parse_args(argv)
    meta = load_meta()
    print(f"publish: {meta['title']} (book_type={meta['book_type']})")
    pages = page_count()
    if pages:
        print(f"  estimated print pages: {pages}")
    print()
    if args.command == "validate-targets":
        print(cmd_validate_targets(meta))
        return 0
    if args.command == "all":
        for cmd in ("copyright", "cover-spec", "pricing", "metadata", "disclaimers", "checklist"):
            fn = {"copyright": cmd_copyright, "cover-spec": cmd_cover_spec,
                  "pricing": cmd_pricing, "metadata": cmd_metadata,
                  "disclaimers": cmd_disclaimers, "checklist": cmd_checklist}[cmd]
            out = fn(meta, args.out_dir)
            print(f"  ✓ {cmd:18} -> {out}")
        print("\nValidate genre targets:")
        print(cmd_validate_targets(meta))
        return 0
    fn = {"copyright": cmd_copyright, "cover-spec": cmd_cover_spec,
          "pricing": cmd_pricing, "metadata": cmd_metadata,
          "disclaimers": cmd_disclaimers, "checklist": cmd_checklist}[args.command]
    out = fn(meta, args.out_dir)
    print(f"  ✓ wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
