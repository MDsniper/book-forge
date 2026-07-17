# Rebuild Prompt — book-forge

> A complete specification prompt for rebuilding the `book-forge` repository from scratch.
> Hand this to an AI coding agent (or use it as a human blueprint) to recreate the project.

---

## 1. Mission

Build **book-forge**: an autonomous book-writing **Agent Skill** (per the Agent Skills standard: a directory containing `SKILL.md` with YAML frontmatter plus bundled `scripts/`, `references/`, and `assets/`). The skill turns a one-line idea into a packaged, sellable book — fiction, nonfiction, or self-help — through six phase-gated stages: **seed → foundation → drafting → revision → export → publish**. It plans, writes, revises, exports (EPUB/DOCX/PDF), produces real publishing artifacts (copyright page, ISBN-stamped KDP/Ingram metadata, cover spec, pricing math, legal disclaimers), and generates a 90-day launch marketing kit.

The skill is **methodology-driven**: it is an orchestration layer for an LLM agent, not a traditional app. Most "logic" lives in markdown instruction files the agent reads on demand; deterministic helpers are pure-stdlib scripts. It must run identically inside at least seven agent hosts (Claude Code, Factory Droid, OpenCode, Kimi CLI, OpenClaw, Hermes Agent, ZCode) because it uses no host-specific APIs — only file reads/writes, Bash, git, and the agent's own subagent/persona capabilities.

License: MIT. Include `LICENSE`, `README.md`, `NOTICE` (attribution: methodology inspired by NousResearch's autonovel; select workflow ideas adapted from authorclaw (MIT) with license preservation; all expression original), and `package.json` (npm package whose only runtime is a pure-stdlib Node ≥18 installer at `bin/cli.mjs`).

## 2. Core model: five layers + one truth-DB

Model every book as six co-evolving files, ordered abstract → concrete:

```
Layer 5: voice.md          — HOW we write (style, tone, register)
Layer 4: world.md          — WHAT exists (fiction: lore/magic/geography; nonfiction: research-bible.md domain map)
Layer 3: characters.md     — WHO acts (fiction) / thesis.md + personas (nonfiction)
Layer 2: outline.md        — beats + foreshadowing ledger (fiction) / argument-thread ledger (nonfiction)
Layer 1: chapters/ch_NN.md — the actual prose
Cross-cutting: canon.md    — WHAT IS TRUE (fiction: hard-facts DB, target 400+ entries; nonfiction: evidence.md, every claim sourced)
```

The layers are **coupled, not a checklist**. Define explicit propagation rules: a change to voice forces re-evaluation of all chapters; a world change forces lore-consistency checks everywhere; a canon change forces chapter checks; etc. When drafting reveals an upstream gap, log a **propagation debt** in `state.json.debts` (`{trigger, affected[], status: pending|in_progress|cleared}`). A phase with pending debts is not finished.

## 3. The universal loop

Every step of every phase is the same loop:

1. **Generate** (or regenerate, targeting the weakest scoring dimension) in an explicit persona.
2. **Evaluate** with the three immune systems (§6) — always on, every phase.
3. **Keep or discard**: improved → `git commit`; worse → `git reset --hard HEAD~1` (foundation/drafting) or `git checkout HEAD -- <chapter>` (revision, single file). Git *is* the discard mechanism and audit trail.
4. **Log** one row to `results.tsv`: `timestamp \t phase \t score \t word_count \t status \t description`.
5. Save `state.json`; next iteration targets the weakest dimension.

Keep on **improvement**, not "good enough" — score thresholds gate *leaving a phase*, not keeping an iteration.

## 4. Phase-gated state machine (one phase per invocation)

The skill is invoked once per phase and returns control to the user between phases. On every invocation: read `state.json` in the cwd → if absent, run **seed**; if present, confirm resume vs. jump to a named phase. Never cascade phases automatically.

### 4.1 `seed`
- Collect or generate: title, `book_type` ∈ {fiction, nonfiction, self-help}, genre/subgenre, targets (default 22 chapters × 3,000 words ≈ 66k words).
- Ask mode: **collaborative** (15-question interview + 4 checkpoints) or **autonomous** (hands-off). Default: collaborative for nonfiction/self-help/memoir, autonomous for fiction. Switchable mid-book.
- No concept? Generate 10 diverse seed concepts, rejecting generic fare (chosen-one, dark-lord, medieval-Europe-plus-elves; vague "mindfulness will fix you"). A good seed has a world-differentiator, central tension, cost/constraint, sensory/human hook.
- Scaffold: write `seed.txt`, copy all templates from `assets/templates/` into the book folder, write `project.yaml` + `state.json` (phase=foundation, debts=[], mode), `git init` + initial commit.
- If collaborative: run the 15-question interview now (questions 6–10 branch by book_type), capturing answers **verbatim** in `interview-answers.md`.
- Print the exact next command (e.g. `/book-forge foundation`).

### 4.2 `foundation` (no prose yet)
Loop until **foundation_score ≥ 7.5 AND (lore_score ≥ 7.0 for fiction OR research_score ≥ 7.0 for nonfiction/self-help)**, max 20 iterations:

1. Build `world.md`/`research-bible.md` → `characters.md`/`thesis.md` → `outline.md` with a **foreshadowing ledger** (`| ID | Planted (ch) | Payoff (ch) | Thread | Status |`; rules: ≥1 scene separation plant→payoff, rule of three references, every thread resolves or is an explained red herring, MICE reverse-order closure) — nonfiction uses an argument/thread ledger with the same closure logic.
2. **Voice discovery sub-loop**: write 5 trial passages in different registers (fiction: mythic/spare/warm/cold/whimsical; nonfiction: authority/confessional/coach/lyrical/reportorial), pick the winner, fill `voice.md` Part 2 with exemplars **and anti-exemplars**.
3. Fiction only: write `MYSTERY.md` — the central secret; **author-only, never loaded into drafting context**.
4. Build `canon.md` (fiction: 400+ hard facts) or `evidence.md` (nonfiction: every claim sourced; if a source can't be verified, mark "unverified" — **never fabricate a citation**).
5. Evaluate, keep/discard, target weakest dimension.
6. Run `scripts/beat_math.py <N> [--mode ...]` to verify structural beats land on real chapters; fix `outline.md` if not.

Collaborative checkpoints (skip when autonomous): **CP1** after world+characters first pass (cap 3 rounds); **CP2** after voice discovery (show all 5 passages, cap 2 rounds); **CP3** after outline + beat validation (cap 4 rounds — the most important gate); **CP4** at revision start. Record each in `state.json.checkpoints_reached`.

### 4.3 `drafting`
For each chapter in outline order, loop until **chapter_score > 6.0** or **5 attempts**:

1. Assemble context **in this exact order**: full `voice.md` → this chapter's beats → next chapter's outline → previous chapter's last ~2,000 chars → `world.md`/`research-bible.md` → `characters.md` → `canon.md` → the chapter-drafting directives from `references/drafting.md`.
2. **Write the FULL chapter** at ≥ target word count. Anti-summarize rules are load-bearing (no "they talked for hours", no time-skip elision of promised scenes, no outline-restating).
3. **Polish** as a separate pass: "produce a REVISED, POLISHED version of THE ENTIRE chapter. Do not shorten. Do not add commentary. Start directly with the prose."
4. Run `scripts/slop_scan.py`, then the LLM judge (separate persona). Final score = judge − slop penalty. Apply stability-trap countermeasures (§5).
5. Score > 6.0 → commit; else discard and retry.
6. Extract new canon/evidence entries from judge output → append to `canon.md`.
7. Append `results.tsv`.

After all chapters: full-manuscript slop sweep; fix recurring AI patterns early (they compound).

### 4.4 `revision`
3–6 cycles, stop on plateau (|Δ novel_score| < 0.3 after ≥ 3 cycles):

0. **CP4 (collaborative only)**: show `arc_summary.md`, full-manuscript slop score, 3 lowest-scoring chapters with judge notes; user notes become priority-weighted briefs.
1. **Adversarial cut analysis** — ruthless-editor persona asks "what would I cut to lose 500 words?" per chapter; classify cuts FAT / REDUNDANT / OVER-EXPLAIN / GENERIC / TELL / STRUCTURAL (expect ~30% OVER-EXPLAIN, ~25% REDUNDANT). The cut list **is** the revision plan.
2. **4-persona reader panel as parallel subagents** (genuine independence): The Editor (prose texture), The Genre/Subject Reader (50+ books/yr), The Writer/Practitioner (structure; nonfiction: methodological rigor), The First Reader (nonfiction swaps in The Skeptic; self-help adds a sensitivity/claimer-of-authority check). **Disagreements are where editorial decisions live** — unanimous praise means re-run.
3. **Consensus items (≥3/4 agreement)** → revision briefs (PROBLEM / WHAT TO KEEP / TARGET) → revise → re-evaluate → keep only if post ≥ pre.
4. **Apply vs. analyze discipline**: analysis passes produce notes; only dedicated apply passes rewrite prose.
5. Full-manuscript slop scan + full-novel judge.
6. **Dual-persona review loop** (max 4 rounds, ideally a fresh session with no writing history): reviewer reads first as critic-for-audience, then as craftsperson-for-author (fiction: literary critic → professor of fiction; nonfiction: reviewer → subject-matter expert). Parse items by severity (major/moderate/minor) and qualification (hedged = qualified). **Stop when**: stars ≥ 4.5 with no major unqualified items; OR stars ≥ 4 with >50% items qualified; OR ≤2 items found.

### 4.5 `export`
Run `scripts/export.py [markdown|epub|docx|pdf...]` (or all): normalize chapter titles; rebuild `outline.md` and `arc_summary.md` from actual chapters; `scripts/assemble.py` concatenates `chapters/*.md` → `manuscript.md`; produce EPUB + DOCX via pandoc and PDF via LaTeX (tectonic preferred, pdflatex fallback) with front/back matter. **Export never fails because a tool is missing** — produce what it can, print install hints (`brew install pandoc`, `brew install --cask mactex` / `cargo install tectonic`, optional `epubcheck`).

### 4.6 `publish`
Run `scripts/publish.py all` (subcommands: `copyright`, `cover-spec`, `pricing`, `metadata`, `disclaimers`, `checklist`, `validate-targets`):

1. **Real copyright page** — ISBN-stamped, disclaimer-correct per book_type (fiction / self-help / memoir / nonfiction variants).
2. **Cover spec sheet** — exact print dimensions from trim size + page count + paper type (spine math), ebook 1600×2560.
3. **Pricing recommendation** — KDP 35%/70% royalty math at candidate prices, print minimum viable price, genre norms.
4. **KDP + IngramSpark metadata templates** — description HTML, 7 keywords, 2–10 categories, comp titles.
5. **Legal disclaimers + risk lint** — auto-flag lyrics trap, memoir defamation risk, self-help overclaiming.
6. **KDP readiness checklist** + human step-by-steps (buy ISBN from Bowker, file copyright, upload to KDP/Ingram, optional ACX audiobook).

Then the writer persona generates the **marketing bundle** from `arc_summary.md`: `blurb.md` (back-cover/Amazon copy), `ad-copy.md` (AMS + Meta + BookBub), `social-posts.md`, `arc-email.md`, plus a **90-day launch timeline** (pre-launch → launch week pricing pulse → KDP Select/KU decision → post-launch cadence). **The skill never uploads anything anywhere** — it produces files + human instructions. Optional cover art via `scripts/image.py`.

## 5. Personas & the stability trap

Persona separation is load-bearing (autonovel uses literally different models; a skill can't, so enforce it via explicit persona switches, harsh calibration, and parallel subagents):

- **Writer**: "literary/prose writer. Follow the voice definition exactly. Hit every beat. Never use banned words. Show, never tell. Metaphors from the character's experience. Write the FULL chapter." (Nonfiction: "expert author and clear explainer.")
- **Judge**: "literary critic and editor. Score what's on the page, not what was intended. Median = 6; 8 = exceptional; 10 does not exist for a first draft. Valid JSON only." (Nonfiction: "editor and fact-checker.")
- **Adversarial editor**: "ruthless. Cuts fat. No sentiment. Quote exactly."
- **Reviewer**: critic-for-audience first, then craftsperson-for-author; honest praise AND named defects.

**Stability-trap countermeasures** (baked into every drafting/revision pass): characters must end truly different (changed, damaged, or having chosen); let bad things stay bad; allow irreversible decisions and real loss; withhold information from the reader; genuine moral ambiguity; vary emotional intensity chapter to chapter; **a choice with no real cost is not a real choice**. Nonfiction variant: don't sand claims into bland unanimity — surface genuine debate, tradeoffs, and contested evidence.

## 6. The three immune systems (quality engine)

### 6.1 Mechanical slop scanner — `scripts/slop_scan.py`
Pure-stdlib Python 3.9+, regex only (no LLM), returns a 0–10 penalty **subtracted from the judge score**. Lexicons: `assets/banned-words.txt` + `assets/ai-tells.txt`, with optional project overrides at `<book>/.book-forge/banned-words.txt` / `ai-tells.txt`. Checks:
- **Tier 1** banned words (delve, utilize, leverage, tapestry, paradigm, myriad, plethora, journey/resonate/elevate/empower, etc.), case-insensitive whole-word.
- **Tier 2** cluster escalation: ≥3 Tier-1 hits per 500 words.
- **Tier 3** filler phrases ("in today's fast-paced world", "plays a crucial role", "a testament to"…).
- Fiction AI-tell regexes (`a sense of \w+`, `couldn't help but feel`, `eyes widened`, `heart pounded in (his|her|their) chest`, `a shiver ran down … spine`, `not just X, but Y`, `the air hung heavy`…).
- Structural tics: em-dash density > 15/1000 words; sentence-length CV < 0.3; transition-opener ratio > 0.3; show-don't-tell patterns ("she felt X").

Calibration: clean chapter 0–1; typical AI draft 3–5; slop-heavy 7+. Usage: `slop_scan.py chapters/*.md [--json] [--book-dir X]`.

### 6.2 LLM judge (separate persona)
Fixed rubric. Fiction chapter dimensions (0–10): prose_quality, voice_adherence, character_voice, beat_coverage, plants_seeded, continuity, canon_compliance (**capped at 6 on any canon violation**), lore_integration, engagement; full-novel adds foreshadowing_resolution, pacing, thematic_coherence. Nonfiction: clarity, voice_adherence, claim_support (**capped at 6 if a claim lacks a source**), structure, engagement, audience_fit.

**Harsh calibration bands**: 9–10 exceptional (name the published books it belongs beside); 7.5–8.9 strong, publishable, any structural problem caps at 7; 6.0–7.4 solid, where most competent AI drafting lands; 4.0–5.9 underbuilt; <4 broken. **Forced gaps**: before scoring any dimension, name its weakest moment + the fix; a dimension without an identified weakness scores max 7. **Forced re-read (FINAL CHECK)**: for any overall > 7, re-read the gap list — if any gap would force mid-draft invention (missing rule, undefined character, unsupported scene), lower the score. Output: strict JSON `{overall_score, dimensions{score, weakest_moment, fix}, new_canon_entries[], summary}`.

### 6.3 Reader/beta panel + dual-persona review
4 personas as parallel subagents (§4.4); consensus ≥3/4 drives briefs; dual-persona review with severity/qualification stopping conditions. Anti-inflation principle throughout: mechanical is objective; the judge is harshly calibrated; the panel must disagree; the writer never judges its own work in the same persona.

Also encode two craft doctrines in the quality reference: **specificity kills slop** ("a jay" not "a bird"; "the smell of hot iron" not "a metallic scent") and **earn every metaphor** from the character's domain (blacksmith → heat/metal; sailor → tides).

## 7. Scripts (all pure-stdlib Python 3.9+, no third-party deps)

- **`slop_scan.py`** — see §6.1.
- **`beat_math.py <chapters> [--mode fiction|story-circle|7-point|nonfiction|self-help]`** — prints the exact chapter each structural beat lands on (Save the Cat percentages, round-up so beats land slightly late rather than early; nonfiction argument arc: Setup→Problem→Framework→Evidence→Application→Synthesis).
- **`assemble.py`** — concatenate `chapters/ch_NN.md` in numeric order → `manuscript.md` with normalized titles + ToC + word counts; `--rebuild-outline` rewrites `outline.md` from chapter headings; `--arc-summary` generates `arc_summary.md` skeleton.
- **`export.py [formats...]`** — Markdown always; EPUB/DOCX via pandoc; PDF via tectonic or pdflatex; graceful-skip with install hints; reads metadata from `project.yaml`/`state.json`.
- **`publish.py <cmd>`** — deterministic publish artifacts (§4.6); minimal hand-rolled YAML scalar parsing (strip quotes/comments) so no pyyaml dependency.
- **`image.py`** — provider-agnostic cover/illustration generator over urllib. Providers: ComfyUI (self-hosted, `COMFYUI_URL`), Google Imagen, OpenAI gpt-image-1, fal.ai, Ideogram, Stability, Replicate. Config precedence: env var → `.book-forge/image-config.json` → `~/.config/book-forge/image-config.json`. Commands: `providers`, `cover` (1600×2560), `cover-print` (trim+bleed), `illustration` (4:3), `concept --variants N`, `generate --w --h`, `brief <type>`, `--dry-run`. Cost-aware (prints estimate before paid generation); text-on-image caveat (only Ideogram/OpenAI render title text reliably; otherwise `includeText:false` and typeset later); never fails when unconfigured — prints setup hints.

## 8. Installer — `bin/cli.mjs`

Pure-stdlib Node ≥18 ES module, zero dependencies, idempotent. A `TARGETS` table of 7 agents, each with install path + detection (config-dir existence or `which <bin>`): ZCode `~/.agents/skills/book-forge`, Claude Code `~/.claude/skills/…`, Factory Droid `~/.factory/skills/…`, OpenCode `~/.config/opencode/skills/…`, Kimi CLI `~/.kimi/skills/…`, OpenClaw `~/.openclaw/skills/…`, Hermes `~/.hermes/skills/writing/…`. Flags: default = detect + install/sync to all detected; `--list` (detect only); `--all`; `--target <name>` or bare positional; `--uninstall`; `-h/--help`. TTY-aware colored output. `package.json` exposes it via `bin.book-forge`; works through `npx github:<user>/book-forge` until published to npm.

## 9. Assets

- **`assets/templates/`** — everything scaffolded into a new book folder at seed time: `state.json`, `project.yaml`, `seed.txt`, `voice.md` (incl. Part 2 voice-definition placeholder), `world.md`, `research-bible.md`, `characters.md`, `thesis.md`, `outline.md` (with ledger table), `canon.md`, `evidence.md`, `MYSTERY.md`, `interview-answers.md`.
- **`assets/banned-words.txt`** (~865 lines) — tiered slop lexicon: Tier 1 single words, Tier 2 fiction-specific, self-help-specific, Tier 3 phrases; comment-organized so both the scanner and humans can extend it.
- **`assets/ai-tells.txt`** (~150 lines) — one regex per line, grouped by category (sensory cliché, physiological, structural tic, telling verb, filter, nonfiction).
- **`assets/image-config.example.json`** — annotated template for all 7 image providers.

## 10. References (14 markdown docs, progressive disclosure)

`SKILL.md` stays the orchestration brain (~270 lines); everything else loads on demand, never preloaded:

- `methodology.md` — 5-layer+canon model, propagation rules/debts, the loop, anti-inflation, stability trap, "done" definitions. **Read at the start of any new book.**
- `foundation.md` — Phase 1 procedure, scoring rubric, voice discovery, MICE closure, exit criteria.
- `drafting.md` — context-window assembly, chapter-drafting directives (Shape/Texture/Structure), anti-patterns, anti-summarize rules, write→polish loop, continuity mechanisms, post-draft sweep, common failures.
- `revision.md` — cut analysis, panel, consensus→briefs, apply-vs-analyze, plateau math, dual-persona stopping conditions.
- `quality.md` — the three immune systems verbatim (slop tiers, judge rubric, harsh calibration, forced gaps/re-read, specificity/metaphor doctrines).
- `craft.md` — Save the Cat (15 beats), 7-Point, Story Circle, MICE, Sanderson's Laws, Scene-Sequel; foreshadowing ledger rules; beat math; framework selection.
- `story-structures.md` — 9 frameworks catalog (Save the Cat, Three-Act, Five-Act/Freytag, Seven-Point, Hero's Journey, Romancing the Beat, Story Circle, 5-Stage Mystery, Martell Thematic) + `none` escape hatch, per-scene spec, try-fail vocabulary, nonfiction argument arcs.
- `nonfiction.md` — research→thesis→TOC→evidence→draft→fact-check pipeline, `[NEEDS SOURCE]` workflow, self-help Concept→Method→Example→Exercise structure, sensitivity pass, failure modes.
- `genres.md` — per-genre voice/structure/benchmarks and word-count norms (fantasy ×2, thriller, mystery, lit-fic, romance, horror, SF; narrative nonfiction, how-to, prescriptive self-help, memoir, business/science/history).
- `collaborative.md` — 15-question interview script (universal 1–5, branched 6–10, universal 11–15), how answers seed each artifact, 4 checkpoint protocols with round caps, what the mode does NOT do.
- `export.md` — assembly, front/back matter, pandoc/LaTeX packaging, KDP readiness.
- `publish.md` — ISBN, copyright pages per type, cover spec math, metadata, pricing, legal, ACX, genre norms table.
- `images.md` — provider selection matrix, cost awareness, aspect presets, brief writing, text-on-image caveat, per-provider setup.
- `launch.md` — 90-day timeline, launch warnings, the 4 marketing assets, comp titles, website/mailing list, pricing pulse, KDP Select decision, post-launch cadence.

## 11. State & tracking files

`state.json` (master tracker): `{title, book_type, genre, phase: seed|foundation|drafting|revision|export|publish|complete, current_focus, iteration, foundation_score, lore_score, research_score, chapters_drafted, chapters_total: 22, words_per_chapter: 3000, novel_score, revision_cycle, collaborative_mode, checkpoints_reached[], debts[]}`. Always save before exiting, even on interruption. `results.tsv`: append-only audit log, one row per keep/discard/cycle.

## 12. Non-negotiable design principles

1. **One phase per invocation** — return control to the user between phases; print the exact next command.
2. **`book_type` routes everything** — never assume fiction; nonfiction/self-help swap world→research-bible, canon→evidence, Mystery→thesis, First Reader→Skeptic, and add fact-check + sensitivity passes.
3. **The three immune systems are always on** — every chapter, every phase.
4. **Git is the keep/discard mechanism** — commits are keeps; hard reset (or single-file checkout in revision) is the discard.
5. **Never fabricate citations** — mark "unverified" instead.
6. **Never upload anything** to KDP/Ingram/social — produce files + human steps only.
7. **Export/publish/image scripts never hard-fail** on missing tools — partial output + install hints.
8. **The reviewer always finds something** — ship on severity/qualification, not zero defects; when critique language shifts from "this has problems" to "these are the costs of the choice," it's done.
9. **Pure stdlib everywhere** — Python 3.9+ scripts with zero deps; Node ≥18 installer with zero deps; the only external tools are git (required), pandoc + a LaTeX engine (optional, for export), and image-provider API keys (optional).
10. **Specificity and earned metaphor** beat any regex — encode them as judge/panel doctrine, not just scanner rules.

## 13. Acceptance criteria

- `npx github:<you>/book-forge --list` detects agents; default run installs/syncs into all detected skill dirs idempotently.
- In any supported agent, invoking the skill in an empty folder runs `seed` and scaffolds the full per-book tree (`seed.txt`, `state.json`, `project.yaml`, templates, `chapters/`, git repo, first commit).
- Each phase honors its numeric gates: foundation ≥7.5 (+lore/research ≥7.0), chapter >6.0 within 5 attempts, revision plateau |Δ|<0.3, dual-persona stop conditions.
- `slop_scan.py` on a known-sloppy sample returns ≥3; on clean prose ≤1.
- `export.py` in a tool-less environment still yields `manuscript.md` + helpful hints; with pandoc+tectonic it yields valid EPUB/DOCX/PDF.
- `publish.py all` emits copyright page, cover spec with correct spine math, pricing table, metadata templates, disclaimers, checklist — all stamped with the book's real metadata.
- `image.py --dry-run cover brief.md` prints the routed provider payload without requiring any API key.
