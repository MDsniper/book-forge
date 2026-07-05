# Publish phase

Take a finished, exported manuscript and turn it into a **sellable book** — complete front matter, real copyright page, ISBN assignment, KDP/IngramSpark-ready files, cover spec, pricing, legal disclaimers, and the launch marketing kit. Run after `export`.

`scripts/publish.py` does the deterministic work (copyright page, cover spec, pricing, KDP metadata templates). The writer persona generates the marketing prose (blurb, description, keywords, ad copy).

## Why this phase exists

A drafted and exported manuscript is **not** a sellable book. The gap is everything that turns prose into a product people can buy: legal protection (copyright, disclaimers), unique identification (ISBN), retailer-ready files (correct trim, margins, embedded fonts, validated EPUB), a cover that signals genre at thumbnail size, pricing that fits the royalty structure, and the metadata + marketing assets that make the book discoverable. Skip these and you have a document; include them and you have a book.

## Procedure

Read project metadata from `project.yaml` / `state.json` (title, author, book_type, genre, page count from the export phase).

1. **Acquire ISBN(s)** — interactive step with the user.
2. **Generate the real copyright page** — `scripts/publish.py copyright`.
3. **Assemble final front + back matter** — writer persona + templates.
4. **Generate the cover spec sheet** — `scripts/publish.py cover-spec`.
5. **Generate KDP + Ingram metadata + marketing bundle** — writer persona.
6. **Pricing recommendation** — `scripts/publish.py pricing`.
7. **Legal disclaimers + risk lint** — auto-selected by `book_type`.
8. **Final KDP readiness report** — `scripts/publish.py checklist`.
9. **Optional: copyright registration, ACX audiobook guide.**

Output goes to a `publish/` folder. Nothing is uploaded anywhere on the user's behalf — this phase produces files and step-by-step instructions for the human steps (buying the ISBN, filing copyright, the KDP upload).

## 1. ISBN — what and how

The International Standard Book Number is a 13-digit identifier unique to **one format/edition**. Each format gets its own: paperback, hardcover, ebook, audiobook each need a separate one (audiobook actually uses ACX/ISRC, not ISBN).

- **United States**: [Bowker / myidentifiers.com](https://www.myidentifiers.com/identify-protect-your-book/isbn/buy-isbn) — the only official US source. **1 ISBN = $125; block of 10 = $295 ($29.50 each); 100 = $575.** ISBNs never expire. Buy the block of 10 — the per-unit economics dominate the moment you publish a second book or a second format.
- **UK & Ireland**: [Nielsen Book](https://www.nielsenedi.com/). **Canada**: Library and Archives Canada (free). **Australia**: Thorpe-Bowker.
- **The free-KDP-ISBN trap**: KDP offers a free print ISBN. **KDP becomes the publisher of record and that ISBN is locked to Amazon** — it cannot be used on IngramSpark or anywhere else. Rule: **buy your own if you want non-Amazon distribution or plan more than one book**; use the free one only for an Amazon-only paperback of a single title.
- **Ebook ISBN**: optional on KDP (Amazon assigns an ASIN automatically); **required by IngramSpark** even for ebooks.
- **Same print format on KDP + IngramSpark**: use the **same** (self-owned) ISBN.

**Step for the user**: `publish.py` prints the Bowker/Nielsen link, asks the user to assign one ISBN per format, then stamps the chosen ISBN(s) onto the copyright page and into the KDP/Ingram metadata templates.

## 2. The copyright page (real, not placeholder)

`scripts/publish.py copyright` generates this from metadata. Three template variants, selected by `book_type`:

### Fiction
```
<TITLE>
<series line if applicable>

Copyright © <YEAR> <AUTHOR>
All rights reserved. No part of this book may be reproduced
or transmitted in any form or by any means, electronic or
mechanical, including photocopying, recording, or by any
information storage and retrieval system, without permission
in writing from the publisher, except by a reviewer who may
quote brief passages in a review.

This is a work of fiction. Names, characters, places, and
incidents either are the product of the author's imagination
or are used fictitiously. Any resemblance to actual persons,
living or dead, events, or locales is entirely coincidental.

ISBN 978-X-XXXX-XXXX-X (paperback)
ISBN 978-X-XXXX-XXXX-X (ebook)

Published by <Imprint>, <City>
<URL>

Cover design by <Designer>
Edited by <Editor>

First Edition / First Printing: <MONTH YEAR>
10 9 8 7 6 5 4 3 2 1
Printed in the United States of America
```

### Self-help / prescriptive nonfiction
Same structure, but the disclaimer becomes:
```
The information in this book is provided for educational and
informational purposes only and is not a substitute for
professional medical, psychological, legal, or financial
advice. The author and publisher disclaim any liability
arising from the use or misuse of the methods described
herein. Consult a qualified professional before making
changes to your health, finances, or routines.
```
Self-help books may also include `Library of Congress Control Number: <LCCN>` (indies can get a PCN free, before publication, via the [PCN program](https://www.loc.gov/programs/cataloging-in-publication/about-this-program/)).

### Memoir
```
This memoir is based on the author's recollections. Some
names, identifying details, and timelines have been changed
to protect the privacy of others. The events are recounted
to the best of the author's memory.
```
Memoir has the **highest defamation/privacy risk** — changing names isn't enough if a real person is still identifiable. Get releases for anyone portrayed negatively or consult a publishing attorney. UK memoirs add: *"The right of <Author> to be identified as the author of this work has been asserted in accordance with the Copyright, Designs and Patents Act 1988."*

## 3. Front & back matter assembly

**Front matter order** (your `assemble.py` should emit these before the manuscript):
1. Half-title (title alone, recto)
2. Title page (title, subtitle, author, series, imprint — recto)
3. Copyright page (verso)
4. Dedication (optional, recto)
5. Epigraph (optional)
6. Table of Contents (required for nonfiction, recommended for fiction)
7. Foreword (someone other than author) **OR** Preface (author, why/how) **OR** Introduction (author, the subject) **OR** Prologue (fiction only, a pre-story scene)

**Back matter order**:
1. Acknowledgments
2. About the Author (with credentials for nonfiction)
3. Also By <Author>
4. Discussion questions (optional)
5. Bibliography / Sources (nonfiction — auto-built from `evidence.md`)
6. Appendices (self-help: exercises, worksheets)
7. Newsletter signup / CTA (the single most important long-term owned asset)

## 4. Cover spec sheet

The skill can't design the cover, but it must hand the user the exact spec. `scripts/publish.py cover-spec` computes from trim + page count + paper:

- **Ebook**: 1600×2560 px, ratio 1.6:1, JPEG/TIFF, ≤5 MB, 300 DPI (min 625×1000).
- **Print**: full-bleed PDF, 300 DPI. Total width = front cover + spine + back cover + 0.375" bleed (0.125" × 3). Total height = trim height + 0.25" bleed.
- **Spine width** = `page_count × paper_thickness`:
  - White paper: 0.002252"/page
  - Cream paper: 0.0025"/page
  - Example: 300 pages cream → 0.75" spine.
- Spine text only viable at ≥100 pages.
- Cover design resources: **Reedsy** marketplace ($625–$1,250 typical), **99designs** ($299–$1,199), **Damonza**, **Deranged Doctor Design** ($500–$2,000). Budget $500+ for a genre-competitive cover from a designer who has shipped in your genre. DIY: Canva, BookBrush, Reedsy Book Editor.

### Generating cover art (optional)

`scripts/image.py` can generate cover art via a configured image API. See `references/images.md` for the full provider list (ComfyUI free/self-hosted, Google Imagen, OpenAI gpt-image-1, fal.ai, Ideogram, Stability, Replicate). Quick path:

```bash
python3 scripts/image.py providers              # what's configured
python3 scripts/image.py brief cover            # scaffold a cover brief
# ... writer persona fills in image-brief-cover.md from voice.md + world.md ...
python3 scripts/image.py cover image-brief-cover.md   # generate, cost-confirmed
```

- **For a cover with title text rendered on it**, use Ideogram or OpenAI gpt-image-1 (the only providers that handle text reliably).
- **For a clean base to typeset manually**, use Flux (fal.ai) or SDXL and add the title in Canva/Photoshop. This is what professional cover designers do — the type is almost never AI-generated.
- The script **never fails** if no provider is configured — it prints setup hints. Cost is shown before generation; `--dry-run` previews without billing.
- AI cover art is a starting point, not a finish line. For a commercially competitive cover, generate comps then hand the chosen direction to a pro designer for final execution.

## 5. KDP / IngramSpark metadata + marketing bundle

`publish.py metadata` emits templates; the writer persona fills them from `arc_summary.md` + `voice.md`:

- **Blurb / back-cover copy** (150–250 words): Hook → Stakes → Payoff, no spoilers. Open with a one-line hook. End on a question/turn, not a resolution.
- **Amazon description** (HTML-formatted, max 4000 chars): `<b>` hook, `<h2>`/`<h3>` sections, `<blockquote>` for review quotes, `<ul>` bullet benefits for nonfiction. (Use the [Kindlepreneur Amazon Book Description Generator](https://kindlepreneur.com/amazon-book-description-generator/) to validate formatting.)
- **7 keywords** (≤50 chars each, long-tail phrases beat single words): research via Amazon's search autocomplete + "customers also searched" suggestions. Don't repeat words KDP already indexes (title, author, category).
- **2–10 BISAC categories**: KDP allows up to 10 via the categorical request system. Find low-competition subcategories by drilling the Amazon best-seller hierarchy — a subcategory with #1 rank <1,000 is reachable for a new book with a launch.
- **Comp titles**: 2–4 recent successful books in your genre for positioning ("for fans of X and Y"). Used in description, newsletter pitches (BookBub, Bargain Booksy), ad targeting.
- **Ad copy variants** (Amazon AMS + Meta): 3 short (1-line hook + link) + 3 long (hook → stakes → CTA), testing different angles.
- **Social posts**: cover reveal, behind-the-book, excerpt drops. Platform by genre: BookTok for YA/romance/fantasy; Instagram for literary/cozy; X for SFF/nonfiction; LinkedIn for business/self-help.
- **ARC email + signup page copy**: ARCs go out 2–4 weeks pre-launch via BookFunnel / Prolific Works / StoryOrigin. Reviews in the first 2 weeks are the largest lever on Amazon's algorithm.

## 6. Pricing recommendation

`scripts/publish.py pricing` computes given format + genre + page count:

**Ebook (KDP royalty structure)**:
- **35% royalty** at any price, OR
- **70% royalty** only for prices **$2.99–$9.99** USD (within file-size/territory limits). At 70%, Amazon deducts a small delivery fee (~$0.06/MB) — negligible for text.
- Below $2.99 or above $9.99 → forced to 35%.
- Genre norms (ebook): romance $2.99–$4.99; thriller/mystery $4.99–$7.99; SFF $4.99–$9.99; literary $7.99–$9.99; nonfiction/self-help $7.99–$14.99 (often >$9.99, accepting 35%).
- **Series-entry strategy**: Book 1 at $0.99 (or perma-free via price-match) to funnel into Books 2–N at full price.

**Print (KDP)**:
- Royalty = `(60% × list price) − print cost`. KDP computes print cost from trim + page count + paper color.
- KDP shows a **minimum viable list price** below which royalty goes negative.
- Typical 70k-word trade paperback (6×9, cream, ~300pp): list **$12.99–$16.99**, royalty ~$2–$4/copy.

**Nonfiction/self-help**: priced higher than fiction. Readers pay for value/outcome. $9.99–$19.99 ebook; $14.99–$29.99 print is normal. A "professional method" book can support $14.99–$24.99 ebook.

## 7. Legal / risk

`publish.py disclaimers` selects by `book_type` + topic scan:

- **Fiction**: standard "work of fiction" disclaimer. **Does not protect you** if real people are identifiable.
- **Self-help / health / finance / legal**: "educational purposes only, not professional advice" disclaimer — material liability shield.
- **Memoir**: name-change notice + the **defamation risk warning** (changing names isn't enough if a real person is identifiable).
- **Lyrics/IP trap**: `publish.py` lints the manuscript for likely lyric quotes (line ending in "♪" or "lyrics:" tags or known song-title references) and warns that **lyric reprint requires permission from the song's music publisher** (not Harry Fox — that's for cover recordings). No statutory rate; publishers can charge anything or refuse. **Workaround: refer to songs by title only — titles aren't copyrightable.**
- **Public domain**: works published before 1929 (in the US) are public domain. Verify — "old" isn't the same as "public domain."
- **Pen names / DBA / tax**: pen name ≠ DBA. KDP does **not** require a DBA — your account uses your legal name + SSN/EIN, the pen name is entered separately per book. Royalties → Form 1099-MISC (US) / 1042-S (non-US); royalty income is subject to 15.3% self-employment tax + income tax, reported on Schedule C. A DBA/LLC matters only if you want to bank or sign contracts under the pen name.
- **Series-title trademark**: a single book title cannot be trademarked (USPTO "title of a single creative work" refusal), but a **series title, pen name, or imprint name CAN** be trademarked if used in commerce.

## 8. Copyright registration (US — optional but high-value)

- File through the **[Electronic Copyright Office (eCO)](https://www.copyright.gov/registration/)** at copyright.gov.
- **Cost**: standard single-work e-filing **$45** (some categories $65).
- **Timing matters**: file **before publication OR within 3 months of first publication** to unlock **statutory damages (up to $150,000/work for willful infringement) and attorney's fees**. Outside that window you can still register but are limited to actual damages.
- **The © notice** is **not legally required** since the US joined the Berne Convention in 1989 — copyright exists automatically on fixation. But the notice is strongly recommended: it bars an "innocent infringer" defense.
- **International**: under Berne, copyright is automatic in all 180+ member countries on fixation. US registration gives US-specific advantages (statutory damages, suit-prerequisite).

## 9. KDP upload — final spec checklist

Before uploading to KDP, the files must pass:

- **Ebook**: validated EPUB (run `epubcheck` — `brew install epubcheck`). EPUB preferred over DOCX/HTML/PDF.
- **Print interior PDF**: correct trim, **mirrored margins** (gutter > outer, sized to page count), **embedded fonts** (verify with a font check), 24-page minimum, ~828-page max (KDP shows the cap per trim).
- **Cover**: full-bleed PDF for print (per spec sheet above) or 1600×2560 JPEG for ebook.
- **Metadata**: title, subtitle, author, 7 keywords, 2–10 categories, description, series info.
- **Pricing**: within the chosen royalty bracket.
- **Content guidelines**: no plagiarism, no copyrighted material without permission, no public-domain repackaging without added value (annotation or ≥10 original illustrations), no keyword stuffing in metadata.

## 10. IngramSpark (parallel print distribution)

Use **alongside** KDP for bookstore/library distribution that Amazon doesn't reach:
- Setup: $0 since May 2023 (per-copy revision fees returning Feb 2026).
- **Returns policy**: the bookstore-eligibility feature. Make the book returnable or bookstores won't stock it. Options: return-and-ship-to-publisher or destroy-in-place.
- **Global Distribution Fee**: 1.875% of wholesale (raised from 1.5% in 2026).
- Standard pattern: **publish print on both** — KDP for Amazon (better royalty there), Ingram for everything else. Use your **own ISBN** so both listings refer to the same edition.

## 11. Audiobook (ACX) — optional

- ACX (Amazon) distributes to Audible, Amazon, Apple Books.
- **Royalty (2026 model)**: exclusive **50%**, non-exclusive **30%**.
- **Narrator compensation**: Pay-for-Production ($50–$400+/finished hour, you keep royalties) OR Royalty Share ($0 upfront, split 50/50, requires exclusive, 7-year contract). 70k-word book ≈ 8–9 finished hours → $400–$3,600+ PFH.
- **File specs**: MP3, 44.1 kHz, mono or stereo, −18 to −23 dB RMS, −3 dB peak max, 3–10 sec room tone at start/end, chaptered files.

## 12. Genre norms reference (validate at seed)

`publish.py validate-targets` checks the user's seed-phase targets against genre norms:

| Genre | Word count | Notes |
|---|---|---|
| Middle Grade | 25,000–55,000 | |
| YA contemporary | 65,000–90,000 | Sweet spot 75–85k |
| YA SFF | 80,000–100,000 | |
| Romance (single-title) | 70,000–100,000 | HEA/HFN mandatory |
| Romantasy | 90,000–120,000 | |
| Thriller / mystery | 80,000–100,000 | Fair-play for mystery |
| Horror | 80,000–100,000 | |
| Epic fantasy | 100,000–130,000 | Debut cap ~120k |
| Science fiction | 90,000–120,000 | |
| Literary fiction | 70,000–100,000 | |
| Memoir | 60,000–90,000 | |
| Self-help / prescriptive | 35,000–60,000 | Shorter, actionable |
| Narrative nonfiction | 70,000–100,000 | |
| Novella | 15,000–40,000 | |

Reader expectations (violating = bad reviews): romance needs HEA/HFN; mystery needs fair-play; thriller needs ticking clock; SFF needs internal consistency; self-help needs promise + method + examples + actionable steps.

## Phase output

The `publish/` folder contains:
- `copyright-page.md` (real, ISBN-stamped, disclaimer-correct)
- `cover-spec.txt` (exact dimensions for ebook + print)
- `pricing.md` (royalty math at candidate prices, recommendation)
- `kdp-metadata.md` (title, subtitle, description HTML, keywords, categories, comps)
- `ingram-metadata.md` (same, Ingram's format)
- `marketing/blurb.md`, `marketing/ad-copy.md`, `marketing/social-posts.md`, `marketing/arc-email.md`
- `legal-disclaimers.md` (the selected disclaimer + risk lint report)
- `checklist.md` (the full pre-publish KDP readiness report)
- `instructions.md` (step-by-step: buy ISBN, file copyright, upload to KDP, optionally Ingram + ACX)

Set `state.json.phase: complete`. Commit. Print the deliverables list and the next steps for the human.
