---
name: book-forge
description: Autonomously plan, write, revise, and export full-length books — fiction, nonfiction, and self-help. Use whenever the user wants to write a novel, novella, memoir, narrative nonfiction, how-to, prescriptive self-help, or any book-length manuscript; to outline or world-build one; to revise/draft existing chapters; or to package a manuscript into EPUB/DOCX/PDF. Trigger on phrases like "write a book", "novel", "outline a story", "book bible", "revise my manuscript", "beta readers", "self-help book", "nonfiction book", "format for KDP".
version: 1.0.0
author: book-forge
license: MIT
tags: [Books, Fiction, Nonfiction, Self-Help, Novel, Writing, Outlining, Revision, EPUB, Publishing]
---

# book-forge

An autonomous book-writing system. Each `/skill book-forge` invocation runs **one phase**, saves state, and tells you what to run next. You steer.

It faithfully ports the methodology of **autonovel** (NousResearch) and folds in the best ideas from **authorclaw**. It writes fiction, nonfiction, and self-help using the same engine, routed by `book_type`.

## How to invoke scripts (IMPORTANT — read this)

Every helper script lives in this skill's `scripts/` directory. The Bash tool's working directory is the **book folder** (the user's `cwd`), NOT the skill folder — so never write `python scripts/foo.py`. Instead, resolve the skill directory first:

- **Claude Code:** scripts are at `${CLAUDE_SKILL_DIR}/scripts/`. Run e.g. `python3 ${CLAUDE_SKILL_DIR}/scripts/slop_scan.py chapters/ch_01.md`.
- **All tools:** if no skill-dir env var is set, the script directory is the absolute path to **this** `SKILL.md`'s parent + `/scripts/`. Compute it once at the start of the phase and reuse it. (ZCode, OpenCode, Kimi, Factory Droid all work this way.)
- Example:
  ```bash
  SKILL_DIR="$(dirname "$(readlink -f "${SKILL_DOCUMENT:-$0}")")" 2>/dev/null || SKILL_DIR="<absolute path to this skill>"
  python3 "$SKILL_DIR/scripts/slop_scan.py" chapters/ch_01.md
  ```
- The Python scripts are **pure stdlib** and run on Python 3.9+. No virtualenv needed.

The four scripts: `slop_scan.py` (slop penalty 0–10), `beat_math.py` (structural beats), `assemble.py` (chapters → manuscript.md), `export.py` (EPUB/DOCX/PDF), `publish.py` (copyright page, cover spec, pricing, metadata, KDP readiness — for the publish phase), `image.py` (cover/illustration generation via ComfyUI, Google Imagen, OpenAI, fal.ai, Ideogram, Stability, or Replicate — for the publish phase).

## The model, in one breath

A book is **five co-evolving layers + one truth-DB**, ordered abstract → concrete:

| Layer | Fiction | Nonfiction / Self-help |
|---|---|---|
| `voice.md` | prose style, tone, register | author voice, rhetorical stance |
| `world.md` | lore, magic, geography, history | domain map, key concepts, terminology |
| `characters.md` | registry, arcs, relationships | personas/archetypes; case-study figures |
| `outline.md` | beats + **foreshadowing ledger** | chapter list + argument/thread ledger |
| `chapters/ch_NN.md` | the prose | the prose |
| `canon.md` | hard-facts DB | **claims/evidence DB** (every claim sourced) |

Changes propagate both ways: a lore change forces an outline check; writing a chapter that reveals a gap forces a world update. Track every pending change as a **propagation debt** in `state.json`. Read `references/methodology.md` before the first run of any book.

## How a phase runs (the loop)

Every phase is the same loop, lifted from autonovel:

1. **Generate / regenerate** the artifact(s) for this step, in persona.
2. **Evaluate** — run the **three immune systems** (always on):
   - *Mechanical:* run `scripts/slop_scan.py` on the prose. It returns a 0–10 penalty.
   - *LLM judge:* a **separate persona** from the writer scores the work against a harsh rubric (median = 6, 8 = exceptional, 10 "does not exist for a first draft"). Apply the FINAL CHECK: if overall > 7, re-read the gap list; if any gap would force the writer to invent something mid-draft, the score is too high — revise it down. Subtract the slop penalty.
   - *Reader panel* (revision only): 4 personas run as **parallel subagents** for genuine independence.
3. **Keep or discard.** Improved → `git add -A && git commit`. Worse → `git reset --hard HEAD~1` (foundation/drafting) or revert the single chapter (revision).
4. **Log** to `results.tsv`, save `state.json`, append any new canon/evidence entries.
5. **Target the weakest dimension** on the next iteration.

**The reviewer always finds something.** The stopping condition is about severity and qualification, not zero defects. When critique language shifts from "this has problems" to "these are the costs of the choice," ship it. Full philosophy in `references/methodology.md`.

## Before you do anything

1. **Read `references/methodology.md`** if this is the first phase of a new book, or any time the user asks "how does this work."
2. Confirm `book_type` (fiction | nonfiction | self-help) — it routes foundation and revision. If unsure, ask.
3. Use **TodoWrite** to lay out the current phase's steps before executing. Update statuses as you go.

## Phase-gated flow

On every invocation:

1. **Read `state.json`** in the current working directory.
   - If absent → run the **seed** entrypoint (below) to scaffold a new book.
   - If present → confirm with the user whether to **resume** the current phase or **jump** to a named phase (`seed | foundation | drafting | revision | export`). Default: resume.
2. **Run that one phase** with all quality machinery on. Do **not** cascade into later phases automatically — return control to the user between phases.
3. **Save `state.json`**, commit keeps to git, append `results.tsv`.
4. Tell the user exactly what to invoke next.

### `seed` — start a new book
- Ask for (or generate) **title**, **book_type** (fiction/nonfiction/self-help), **genre/subgenre**, and **targets** (chapter count, words/chapter, total). Defaults: 22 chapters × 3000 words ≈ 66k words.
- If the user has no concept, generate **10 diverse seed concepts** (reject generic fare: chosen-one, dark lord, medieval-Europe-plus-elves for fiction; vague "mindfulness will fix you" for self-help). A good seed has a **world-differentiator, central tension, cost/constraint, sensory/human hook**. Let the user pick or remix.
- Write `seed.txt`, copy templates from `assets/templates/` into the cwd, write `project.yaml` and `state.json` (phase=`foundation`, debts=[]), `git init`, initial commit.
- Print the next command: `/skill book-forge foundation`.

### `foundation` — build the substrate (no prose yet)
Read `references/foundation.md` for the full procedure. Loop until **foundation_score ≥ 7.5 AND (lore_score ≥ 7.0 for fiction, OR research_score ≥ 7.0 for nonfiction/self-help)**, max 20 iterations:

1. `world.md` (or `research-bible.md`) → `characters.md` → `outline.md` (with **foreshadowing ledger** for fiction / **thread ledger** for nonfiction) → **voice discovery sub-loop** (write 5 trial passages in different registers — mythic/spare/warm/cold/whimsical for fiction, or authority/confessional/coach/lyrical/reportorial for nonfiction — pick the best, fill `voice.md` Part 2 with exemplars + anti-exemplars).
2. For fiction only: write `MYSTERY.md` (the central secret the reader discovers — **author-only, never loaded into drafting context**).
3. Build `canon.md` (fiction: target 400+ hard-fact entries; nonfiction/self-help: every claim sourced to evidence, **no fabricated citations** — if a source can't be verified, write "unverified" rather than invent one).
4. Evaluate. Keep if improved, else `git reset --hard HEAD~1`. Target the weakest dimension next.
5. Run `scripts/beat_math.py` to confirm structural beats land on real chapters; fix `outline.md` if they don't.
- Print: `/skill book-forge drafting`.

### `drafting` — write the book, forward progress over perfection
Read `references/drafting.md` for the full procedure. For each chapter in outline order, loop until **chapter_score > 6.0** or **5 attempts**:

1. **Assemble the context window** (in order): full `voice.md` → this chapter's outline beats → next chapter's outline (continuity) → previous chapter's last ~2000 chars → `world.md`/`research-bible.md` → `characters.md` → `canon.md` → the 24 drafting instructions in `references/drafting.md`.
2. **Write** the FULL chapter. Anti-summarize rules are load-bearing — see `references/drafting.md`. Write at least the target word count.
3. **Polish** in a separate pass: "produce a REVISED, POLISHED version of THE ENTIRE chapter. Do not shorten. Do not add commentary. Start directly with the prose."
4. Run `scripts/slop_scan.py`, then the LLM judge (separate persona). Score = judge − slop_penalty. Apply stability-trap countermeasures from `references/quality.md`.
5. Score > 6.0 → keep (commit), else discard and retry.
6. **Extract new canon/evidence entries** from the judge output → append to `canon.md`.
7. Append `results.tsv`.
- After all chapters: run a full-manuscript slop sweep; fix recurring AI patterns early (they compound).
- Print: `/skill book-forge revision`.

### `revision` — the deep pass
Read `references/revision.md` for the full procedure. **3–6 cycles**, stop on plateau (|Δ score| < 0.3 after ≥ 3 cycles):

1. **Adversarial cut analysis** — as a ruthless editor, ask "what would I cut to lose 500 words?" What you'd cut **is** the revision plan. Expect ~30% OVER-EXPLAIN, ~25% REDUNDANT.
2. **Reader/beta panel** — 4 personas as **parallel subagents**:
   - **The Editor** (prose texture, subtext, sentence craft)
   - **The Genre/Subject Reader** (50+ books/year in this genre/field; pacing, payoff)
   - **The Writer/Practitioner** (structure, beats, foreshadowing; or, for nonfiction, methodological rigor)
   - **The First Reader** (general reader; emotional, no craft jargon)
   - **Disagreements between readers are where editorial decisions live.** Nonfiction swaps in **The Skeptic** for The First Reader; self-help adds a **sensitivity/claimer-of-authority** check.
3. **Consensus items** (≥ 3/4 agreement) → revision priorities. For each: write a brief (PROBLEM / WHAT TO KEEP / TARGET) → revise → re-evaluate → keep if post ≥ pre else revert.
4. **Apply vs. analyze discipline:** analysis passes produce notes; only the dedicated **apply** pass rewrites prose. Don't conflate them.
5. Run `scripts/slop_scan.py` + full-novel judge → novel-level score.
6. **Dual-persona review loop** (max 4 rounds): send the full manuscript to a reviewer prompted as *literary critic then professor of fiction* (fiction) or *reviewer then subject-matter expert* (nonfiction). Parse items with severity (major/moderate/minor) and qualification (hedged language = qualified). **Stop when:** stars ≥ 4.5 with no major unqualified items; OR stars ≥ 4 with > 50% items qualified; OR ≤ 2 items found.
- Print: `/skill book-forge export`.

### `export` — package it
Read `references/export.md` for the full procedure. Run `scripts/export.py <format>` (or all) which:
1. Normalizes chapter titles, rebuilds `outline.md` and `arc_summary.md` from the actual chapters.
2. Concatenates `chapters/*.md` → `manuscript.md` (via `scripts/assemble.py`).
3. Produces **EPUB + DOCX** via pandoc, **PDF** via LaTeX (tectonic or pdflatex), with front/back matter.
4. **Never fails** because a tool is missing — produces what it can and prints install hints (`brew install pandoc`, `brew install --cask mactex` or `cargo install tectonic`).
- Print: `/skill book-forge publish`.

### `publish` — make it sellable
Read `references/publish.md` for the full procedure. Turns an exported manuscript into a sellable book. Run `scripts/publish.py all` (or per-command: `copyright`, `cover-spec`, `pricing`, `metadata`, `disclaimers`, `checklist`) which generates:
1. **Real copyright page** (ISBN-stamped, disclaimer-correct for the book_type: fiction / self-help / memoir / nonfiction).
2. **Cover spec sheet** (exact print-cover dimensions from trim + page count + paper; ebook 1600×2560; spine math).
3. **Pricing recommendation** (KDP 35%/70% royalty math at candidate prices; print minimum viable price; genre norms).
4. **KDP + IngramSpark metadata templates** (description HTML, 7 keywords, 2–10 categories, comp titles).
5. **Legal disclaimers + risk lint** (lyrics trap, memoir defamation, self-help overclaiming auto-flagged).
6. **KDP readiness checklist** + step-by-step human instructions (buy ISBN from Bowker, file copyright, upload to KDP/Ingram, optionally ACX).
Then the writer persona generates the **marketing bundle** (blurb, ad copy, social posts, ARC email) from `arc_summary.md` — see `references/launch.md` for the 90-day launch timeline.
- The skill **never uploads anything** to KDP/Ingram/social on the user's behalf. It produces the files + the human steps.
- Print: book is complete. Set `state.json.phase: complete`.

## The personas (you play all of them)

Switch persona explicitly before each role. The separation is the point — autonovel uses *literally different models* to avoid self-congratulation; a skill can't, so we preserve it through harsh calibration, persona separation, and parallel subagents for the panel.

- **Writer** (drafting/revising): "literary/prose writer. Follow the voice definition exactly. Hit every beat. Never use words from the banned list. Show, never tell. Metaphors come from the character's experience. Write the FULL chapter — no truncation, summary, or skipping ahead."
- **Judge** (evaluating): "literary critic and editor. Evaluate fiction/prose with precision. Score what's on the page, not what the writer intended. Harsh calibration: median = 6, 8 = exceptional, 10 does not exist for a first draft. Always respond in valid JSON."
- **Adversarial editor** (cut analysis): "ruthless editor. You cut fat. You have no sentiment about good-enough sentences. Quote exactly. Classify cuts: FAT / REDUNDANT / OVER-EXPLAIN / GENERIC / TELL / STRUCTURAL."
- **Reviewer** (final): "first a literary critic (a newspaper book review), then a professor of fiction / subject expert giving specific actionable notes. Be fair but honest. You don't *have* to find defects."
- **Nonfiction variants**: Writer → "expert author and clear explainer"; Judge → "editor and fact-checker"; Reviewer → "reviewer then subject-matter expert."

## Stability trap (read this before drafting)

AI's worst tendency is favoring stability over change. Countermeasures, baked into every drafting and revision pass:
- Characters must end **truly different** — changed, damaged, or having chosen.
- Let bad things **stay bad**. Don't auto-repair.
- Allow irreversible decisions and real loss.
- Withhold information from the reader (information economy).
- Create genuine moral ambiguity.
- Vary emotional intensity chapter to chapter.
- **If a choice has no real cost, it's not a real choice.**
For nonfiction/self-help: don't sand every claim into bland unanimity — surface genuine debate, real tradeoffs, and where the evidence is uncertain.

## Anti-slop (always on)

Read `references/quality.md` for the full system. The non-negotiables:
- Run `scripts/slop_scan.py` on every chapter and on the full manuscript before scoring.
- Banned words and AI-tell regex patterns live in `assets/banned-words.txt` and `assets/ai-tells.txt` — the script reads them. Add book-specific bans to the project's `.book-forge/banned-words.txt` and the script picks them up.
- **Specificity kills slop** ("a jay" not "a bird"; "the smell of hot iron" not "a metallic scent").
- **Earn every metaphor** from the character's domain (blacksmith → heat/metal; sailor → tides).

## Reference loading (progressive disclosure)

Read on demand — do **not** preload all of these:

- `references/methodology.md` — the 5-layer + canon model, the modify-evaluate-keep loop, propagation debts, stability trap, anti-inflation philosophy. **Read at the start of any new book.**
- `references/foundation.md` — full Phase 1 procedure, scoring rubric, voice discovery sub-loop, MICE closure, beat-math usage.
- `references/drafting.md` — the 24 drafting instructions verbatim, context-window assembly, anti-summarize rules, canon extraction.
- `references/revision.md` — adversarial cut analysis, 4-persona panel, brief→revision, apply vs. analyze discipline, plateau math, dual-persona review stopping conditions.
- `references/quality.md` — the three immune systems verbatim: slop tiers, judge rubric with harsh calibration, reader personas, disagreements-as-decisions.
- `references/craft.md` — plotting frameworks (Save the Cat, Story Circle, MICE, Sanderson), foreshadowing ledger rules, structural beat math, scene-sequel.
- `references/nonfiction.md` — nonfiction & self-help adaptation: research→thesis→TOC→evidence→draft→fact-check, the evidence DB, sensitivity pass.
- `references/export.md` — Markdown assembly, pandoc EPUB/DOCX, LaTeX PDF, front/back matter, KDP readiness.
- `references/genres.md` — genre-specific voice/structure defaults (fantasy, thriller, lit-fic, memoir, how-to, prescriptive self-help, narrative nonfiction).
- `references/publish.md` — the publish phase: ISBN, copyright page, KDP/Ingram upload specs, cover specs, pricing, legal, ACX. **Read before the publish phase.**
- `references/images.md` — cover & illustration generation: provider setup (ComfyUI free, Google Imagen, OpenAI, fal.ai, Ideogram, Stability, Replicate), brief writing, text-on-image caveats, cost awareness. **Read before generating images.**
- `references/launch.md` — the 90-day launch orchestrator, marketing asset bundle, ad copy specs, ARC/comp-title/website strategy.
- `references/story-structures.md` — the 9 plotting frameworks catalog (Save the Cat, Three-Act, Five-Act, Seven-Point, Hero's Journey, Romancing the Beat, Story Circle, 5-Stage Mystery, Martell Thematic) with beat positions and genre recommendations.

## Install / sync (npx)

This skill is an npm package. To install or re-sync into all detected agents:

```
npx book-forge            # auto-detect + install to all detected agents
npx book-forge --list     # show detection, install nothing
npx book-forge --all      # install to ALL targets even if undetected
npx book-forge claude     # install to one named target
npx book-forge --uninstall
```

Pure stdlib Node (>=18), no dependencies. After install, invoke from any agent: `/book-forge <phase>` (Claude Code / Factory Droid / ZCode), `/skill:book-forge` (Kimi), or by description (OpenCode / OpenClaw / Hermes).

## state.json (the master tracker)

```json
{
  "title": "...",
  "book_type": "fiction",
  "genre": "...",
  "phase": "foundation",
  "current_focus": null,
  "iteration": 0,
  "foundation_score": 0.0,
  "lore_score": 0.0,
  "research_score": 0.0,
  "chapters_drafted": 0,
  "chapters_total": 22,
  "words_per_chapter": 3000,
  "novel_score": 0.0,
  "revision_cycle": 0,
  "debts": []
}
```

`phase` is `seed | foundation | drafting | revision | export | publish | complete`. Always save before exiting, even on interruption. `debts` entries look like `{"trigger": "ch_07: needs teleport rules", "affected": ["world.md","ch_03.md"], "status": "pending"}`. Clear a debt when its propagation check is done.

## results.tsv (the audit log)

Append one row per keep/discard/cycle, tab-separated:
`timestamp \t phase \t score \t word_count \t status \t description`

## Final reminders
- One phase per invocation. Return control between phases.
- `book_type` routes everything — never assume fiction.
- The three immune systems are always on.
- Git commits are keeps; `git reset --hard HEAD~1` is the discard.
- The reviewer always finds something — ship on severity/qualification, not zero defects.
- If pandoc/LaTeX are missing, export what you can and print the install hint. Never fail.
