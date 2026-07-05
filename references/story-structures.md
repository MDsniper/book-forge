# Story structures catalog

Ported from authorclaw's `gateway/src/services/story-structures.ts`. Each structure has beat definitions with expected positions (% of the book), keywords, must-have flags, and recommendations by genre. Use during `foundation` to pick a primary framework, and during `drafting` to validate beat coverage.

## How to choose

The `recommend()` heuristic (no LLM): +0.6 for genre match, −0.4 for "works less well for," +0.15–0.2 for description-keyword matches. Always surfaces `none` prominently for literary/experimental. Three-act is the fallback default at fitScore 0.5.

For most commercial fiction, **Save the Cat!** is the spine. For romance, use **Romancing the Beat** (not Save the Cat). For mystery, use **5-Stage Mystery**. For theme-heavy literary work, **Martell Thematic**.

## The 9 structures

### 1. Save the Cat! (Blake Snyder) — 15 beats
The default for commercial fiction. Beats at fixed % positions:
- **Opening Image** (0–1%) — the "before" snapshot.
- **Theme Stated** (~5%) — someone says the theme, often obliquely.
- **Set-Up** (1–10%) — protagonist's flawed world.
- **Catalyst** (~11%) — inciting incident, must be **external**.
- **Debate** (11–23%) — protagonist resists.
- **Break into Two** (~23%) — protagonist commits; **must be a choice**.
- **B Story** (~27%) — the relationship/mirroring subplot begins.
- **Fun and Games** (26–50%) — the "promise of the premise."
- **Midpoint** (~50%) — **must reverse trajectory** (false victory or false defeat).
- **Bad Guys Close In** (50–68%) — external + internal pressure compounds.
- **All Is Lost** (~68%) — lowest point; **must include some form of death**.
- **Dark Night of the Soul** (68–77%) — protagonist processes.
- **Break into Three** (~77%) — the synthesis.
- **Finale** (77–97%) — protagonist, changed, executes the new plan.
- **Final Image** (~99%) — the "after" snapshot; **must mirror the Opening Image**.

Act structure: Act I 0–23%, Act II 23–77%, Act III 77–100%. Recommended for: fantasy, thriller, SFF, YA. Works less well for: romance (use Romancing the Beat), experimental literary.

### 2. Three-Act Structure — 7 beats
The fallback default. Act 1 (25%): Setup, Inciting Incident, 1st Plot Point. Act 2A (25%): Rising Action, Fun & Games, Midpoint. Act 2B (25%): Complications, All Is Lost, Dark Moment. Act 3 (25%): Climax, Resolution, Denouement. Universal; works for everything but optimizes for nothing.

### 3. Five-Act / Freytag's Pyramid — 6 beats
Climax at **50%**, falling action on the back half. Beats: Exposition, Rising Action, Climax (50%), Falling Action, Resolution, (optional Catastrophe for tragedy). Recommended for: tragedy, classical literary work. Works less well for: commercial pacing (climax at 50% feels early to modern readers).

### 4. Seven-Point Story Structure (Dan Wells) — 7 beats
**Designed for plotting backward** — decide the Resolution first, then Hook, then Midpoint, then fill in. Beats: Hook, Plot Turn 1, Pinch 1, Midpoint, Pinch 2, Plot Turn 2, Resolution. Recommended for: tightly-plotted novellas, mystery, short fiction. The mirror property: Hook and Resolution should be exact opposites.

### 5. Hero's Journey (Campbell / Vogler) — 12 stages
Ordinary World → Call to Adventure → Refusal → Mentor → Crossing Threshold → Tests/Allies/Enemies → Approach → Ordeal → Reward → The Road Back → Resurrection → Return with Elixir. Recommended for: quest fantasy, adventure, epic SFF. Works less well for: contemporary fiction, intimate character work.

### 6. Romancing the Beat (Gwen Hayes) — 10 beats
**Use this for romance, not Save the Cat.** Beats: Meet Cute, Cute Meet (setup), Sexy Invitations (tentative connection), Sexy Time 1 (low stakes intimacy), Conflict (the lie/wound surfaces), Black Moment (the breakup), Lick Wounds (separate reflection), Epiphany (the realization), Sexy Time 2 (high stakes intimacy), Happy Ever After. Mandatory: **HEA or HFN ending** — romance readers downrate books without one.

### 7. Story Circle (Dan Harmon) — 8 stages
You (comfort) → Need → Go (enter unfamiliar) → Search (adapt) → Find (get what they wanted) → Take (pay the price) → Return (to familiar, changed) → Change. **Fractal** — applies to the whole novel, each act, each chapter. Top half = order/comfort; bottom half = chaos/unknown. Recommended for: literary fiction, character-driven work, episodic structures.

### 8. 5-Stage Mystery — 10 beats
Setup → Investigation → Complications → False Solution → True Solution, with a **red herring at ~50%** (the Midpoint). Beats: The Crime, The Detective Engaged, The First Trail, The Red Herring, Complications, Suspect Elimination, The Wrong Answer, The Twist, The Reveal, The Explanation. **Mandatory: fair-play** — the reader must have all clues needed to solve it. Concealed info = betrayal of the contract.

### 9. Martell Thematic (William Martell) — 9 beats
**Theme as spine.** Protagonist holds a flawed worldview; antagonist embodies the **opposite extreme**. Climax = the synthesis of the two. Beats: Thematic Statement, Protagonist's Flawed View, Antagonist's Opposite View, The Clash, Doubt, Reinforcement, The Crisis, The Synthesis, The Resolution. Recommended for: idea-driven SFF, literary fiction, theme-heavy nonfiction. Works less well for: pure commercial pacing.

### `none` (escape hatch)
For experimental/literary work that deliberately rejects structural scaffolding. The skill still tracks the foreshadowing/thread ledger and the stability-trap countermeasures — structure is optional, consistency isn't.

## Per-scene spec (regardless of framework)

When the outline is at scene-level (recommended for high-stakes chapters), each scene specifies:

- **POV Character** — whose head (fiction) or whose voice (nonfiction anecdote).
- **Goal** — what the POV character wants this scene.
- **Conflict** — what stands in the way.
- **Outcome** — yes / no / yes-but / no-and. (Avoid pure "yes" — it kills tension.)
- **Emotional Arc** — start → end emotion (should change).
- **Plot Threads** — which ledger IDs advance this scene.
- **Word Count Target** — usually a fraction of the chapter target.

## Scene-Sequel rhythm (Dwight Swain)

Alternating: **Scene** (Goal → Conflict → Disaster) followed by **Sequel** (Reaction → Dilemma → Decision). Pure scene is exhausting; pure sequel is static. The rhythm is the book's pulse.

## Try-fail cycle vocabulary (autonovel)

`yes-but` / `no-and` / `no-but` / `yes-and`. **Rule: 60%+ of middle scenes should be `yes-but` or `no-and`.** `yes-and` is rare — save for climax.

## Beat math (autonovel / authorclaw shared)

For a N-chapter book, structural beats land at:
- Setup ends: `round(N × 0.12)`
- Inciting Incident: `round(N × 0.20)`
- Midpoint: `round(N × 0.50)`
- Twist / All Is Lost: `round(N × 0.75)`
- Climax: last 2 chapters

Run `python scripts/beat_math.py <N>` (or `--mode nonfiction` for the argument arc). The script flags collisions (two beats sharing a chapter).

## Frameworks for nonfiction (argument arc)

When `book_type ∈ {nonfiction, self-help}`, the structure is the **argument arc**, not a story arc:
- Setup (why this matters) — ~10%
- Problem (current state) — ~20%
- Framework (the lens) — ~35%
- Evidence (the case) — ~65%
- Application (what to do) — ~85%
- Synthesis (tying together + steelman) — last 1–2 chapters

Self-help adds a **Core Method** beat at ~25% (the technique the book teaches). Each Application chapter uses **Concept → Method → Example → Exercise** structure.

## State the framework choice

In `outline.md`, line 1: `**Framework:** <name>`. Every later phase (drafting, revision) reads this to know which rules apply. Hybrid frameworks are fine — state the hybrid rule (e.g., "Save the Cat! spine + MICE for thread closure + Romancing the Beat for the romance subplot").
