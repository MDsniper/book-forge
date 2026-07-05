# Foundation phase

Build the substrate. No prose yet. Loop until `foundation_score ≥ 7.5` AND (`lore_score ≥ 7.0` for fiction, OR `research_score ≥ 7.0` for nonfiction/self-help), max 20 iterations.

## Why foundation matters

Every chapter is written against the foundation. A weak foundation forces the writer to invent under pressure mid-chapter, which is where AI storytelling collapses. Spend the iterations here.

## Procedure (one iteration)

1. **World / research bible.** Regenerate `world.md` (fiction) or `research-bible.md` (nonfiction). For fiction, lore is weighted **40% of foundation score** — magic system with hard rules/costs and societal implications, history that creates present tensions (not decoration), distinct geography/culture, deep interconnection, iceberg depth (more implied than stated). For nonfiction, the research bible covers topic scope, target audience, core thesis, key terminology, and the field's contested questions.

2. **Characters.** `characters.md`: a registry of every named character with role, arc (start state → end state, must be a real change), relationships, voice markers. Nonfiction: case-study figures, exemplar personas, or (self-help) the archetypes of reader the book addresses.

3. **Outline.** `outline.md` in two parts:
   - **Part 1:** chapter-by-chapter beats. Use a plotting framework (see `craft.md`). For nonfiction, the chapter list follows the argument arc.
   - **Part 2:** the **foreshadowing ledger** (fiction) or **argument/thread ledger** (nonfiction). Each row: ID, planted-chapter, payoff-chapter, thread, status.

4. **Beat math check.** Run `python scripts/beat_math.py <chapter_count>` and confirm the structural beats (Setup, Inciting Incident, Midpoint, Twist, Climax) land on real chapters. Adjust `outline.md` if a beat lands between chapters or lands wrong. For nonfiction, the equivalent is the argument-arc beat map (Setup → Problem → Framework → Evidence → Application → Synthesis).

5. **Voice discovery sub-loop.** Write 5 short trial passages (~400 words each) of the same scene/argument in different registers:
   - **Fiction:** mythic, spare, warm, cold, whimsical.
   - **Nonfiction:** authoritative, confessional, coach, lyrical, reportorial.
   Evaluate each against (a) distinctiveness, (b) match to the book's subject, (c) sustainability over a full book. Pick the winner. Fill `voice.md` **Part 2** (the discovered voice) with: the chosen register, 2–3 exemplar passages written in it, and 2–3 **anti-exemplars** showing what to avoid (the registers you rejected and why).

6. **Mystery / thesis file.**
   - **Fiction:** write `MYSTERY.md` — the central secret the reader discovers. **Author-only. Never loaded into the drafting context.** The mystery must emerge from world + characters, never stated explicitly until the reveal. This forces information economy.
   - **Nonfiction:** write `thesis.md` — the single sentence the whole book argues, plus the strongest possible version of the opposing view (steelman). The book must engage the steelman, not strawman it.

7. **Canon / evidence DB.**
   - **Fiction `canon.md`:** every established hard fact — geography, timeline, magic rules, character facts, in-story events that cannot be undone. Each entry falsifiable, with a source (which file/scene established it). **Target: 400+ entries before exiting foundation.** A canon violation caps a chapter's `canon_compliance` score at 6.
   - **Nonfiction `evidence.md`:** every claim the book will make, each with a source. **No fabricated citations.** If you cannot verify a source, mark it `unverified` and either find a real one or cut the claim. This is non-negotiable — authorclaw treats fabrication as a hard failure and so do we.

8. **Cross-layer consistency checks.** Before evaluating:
   - Outline references only lore/claims that exist in `world.md` / `research-bible.md`.
   - Character arcs align with outline beats.
   - Character abilities match magic-system rules (fiction).
   - Foreshadowing/thread ledger balances (every plant has a payoff or a deliberate red-herring flag).
   - Canon/evidence is fully populated; no claim is unsourced.

9. **Evaluate.** Foundation-mode judge scores these dimensions (fiction weighting):
   - Lore / worldbuilding — **40%**
   - Character — **30%**
   - Structure (outline + ledger) — **20%**
   - Craft (voice coherence) — **10%**
   `foundation_score` is the weighted sum. `lore_score` is the lore dimension alone (used as a gate because weak lore is the most common foundation failure). Nonfiction rebalances: Research/thesis 40%, Structure 25%, Audience-fit 20%, Voice 15%.

10. **Keep or discard.** If `foundation_score` improved → `git add -A && git commit -m "foundation iter N: score X.XX (target weakest: <dim>)"`. If worse → `git reset --hard HEAD~1`. Either way, append `results.tsv`.

11. **Target the weakest dimension** on the next iteration. The foundation prompt for iteration N+1 explicitly names the weakest dimension and the specific gaps the judge identified.

## Harsh calibration (apply at every evaluation)

> **9–10:** Could not improve this with a month of focused editorial work. Reserve 10 for work that **surprises** you.
> **7–8:** Strong. A score of 8+ requires **zero major gaps**.
> **5–6:** Competent but unremarkable. The median AI output.
> **Below 5:** Real problems.

**FINAL CHECK (always apply):** If your overall_score is above 7, re-read your gap lists. If any gap describes a problem that would force a writer to stop and invent something during drafting, your score is too high. Revise down.

## MICE closure (fiction)

Threads close in **reverse order of opening**, like nested HTML tags. MICE = Milieu, Idea, Character, Event. If you open a Milieu thread (a journey), then an Idea thread (a question), then a Character thread (an arc), you must close them Character → Idea → Milieu. Closing out of order is a structural defect the foundation evaluator should catch and the outline should fix before drafting begins.

## Exit criteria

- `foundation_score ≥ 7.5`
- `lore_score ≥ 7.0` (fiction) OR `research_score ≥ 7.0` (nonfiction)
- Canon ≥ 400 entries (fiction) OR every claim sourced with zero fabricated citations (nonfiction)
- Foreshadowing/thread ledger balanced
- No pending propagation debts
- Beat math confirmed against `outline.md`

Then: write the foundation-complete summary to `state.json`, set `phase: drafting`, and tell the user to run `/skill book-forge drafting`.
