# Drafting phase

Write the book. Forward progress over perfection — chapter_score > 6.0 is good enough; revision is for polish. For each chapter in outline order, loop until score > 6.0 or 5 attempts.

## Context window assembly (do this exactly, in this order)

The chapter prompt assembles, in order:

1. **VOICE DEFINITION** — full `voice.md` (Part 1 guardrails + Part 2 discovered voice with exemplars and anti-exemplars).
2. **THIS CHAPTER'S OUTLINE** — every beat, every foreshadowing plant/payoff due this chapter. "Hit every beat."
3. **NEXT CHAPTER'S OUTLINE** — for continuity. Know where you're going so this chapter ends pointing at it.
4. **PREVIOUS CHAPTER'S ENDING** — last ~2000 chars of `chapters/ch_(N-1).md`. Continue from here; don't re-establish what the last chapter established.
5. **WORLD BIBLE** — `world.md` (fiction) or `research-bible.md` (nonfiction).
6. **CHARACTER REGISTRY** — `characters.md`.
7. **CANON / EVIDENCE** — `canon.md` (fiction) or `evidence.md` (nonfiction). Every fact you write must be consistent with this; nonfiction claims must trace to a sourced entry.
8. **THE 24 WRITING INSTRUCTIONS** (below).

For nonfiction, also include the **steelman** from `thesis.md` so the chapter engages the opposing view honestly rather than strawmanning it.

## The chapter-drafting directives

Read these into the writer persona before every draft. These are book-forge's own directives, organized into four groups: shape, texture, structure, and anti-patterns. They are the difference between a chapter and a summary.

### Shape — what the chapter must accomplish

- **Length:** write the full target word count (default 3000). Do not summarize, truncate, or skip ahead. If running short, expand scenes — add dialogue beats, sensory moments, interior reaction — never summary.
- **POV:** stay locked to one point-of-view character per chapter (fiction). For nonfiction, hold the chosen register from `voice.md` Part 2 without drifting.
- **Beat coverage:** every beat in the chapter's outline entry must appear. A beat compressed to a single sentence instead of lived in a scene counts as missed.
- **Threads:** every foreshadowing plant due this chapter must be planted; every payoff due must land.

### Texture — how the prose must feel

- **Sensory ground:** every scene anchors in at least three senses. Not just sight — smell, touch, taste, sound.
- **Clean vocabulary:** no banned words (`assets/banned-words.txt` + project overrides) and no AI-tell patterns (`assets/ai-tells.txt`).
- **Sentence-length variation:** mix long, medium, and short. Aim for a sentence-length coefficient of variation ≥ 0.3 (the slop scanner enforces this). Three short sentences in a row are a deliberate choice; ten are a tic.
- **Earned figurative language:** metaphors and similes draw from the POV character's domain (a blacksmith reaches for heat and metal; a sailor for tides and line). Generic stock comparisons are slop.
- **Show, don't tell emotion (fiction):** behavior and physiology on the page; the reader infers the feeling. Naming an emotion ("she was afraid") is a tell — replace it with what fear actually does to her body and choices.
- **Trust the reader:** don't explain what a scene meant. Let it land.

### Structure — how the chapter must move

- **Open in scene:** drop the reader into action or dialogue. No weather openers, no dream sequences, no waking up — unless the moment is load-bearing for the story.
- **End on a turn:** close on an image, a question, a shift, or a quiet beat — never a recap. The last sentence is what readers carry into the next chapter.
- **Scene-to-summary ratio:** roughly 70% in-scene (moment-by-moment action and dialogue), 30% reflection or summary. Invert that and the chapter reads as reportage.
- **Section breaks:** at most two per chapter, used only for genuine time or location jumps — never as a rhythm crutch.

### Anti-patterns to watch for

These recur in unguarded prose. None is forbidden — each is a *budget* to spend deliberately, not an infinite resource.

- **The rule of three abused:** "X. Y. Z." lists and "X and Y and Z" triads. Once per chapter is dramatic; four times is mechanical.
- **Negation as emphasis:** "She did not look back." Effective once; diluted if it appears five times.
- **Rehearsed thought:** "He thought about his father" — narrate the thought itself (as fragment, action, or dialogue) instead of announcing it.
- **The "the way" simile connector:** "the way his mother used to" — twice per chapter is plenty.
- **Telling after showing:** the worst habit. Once a scene has demonstrated something, the narrator must not restate it. Trust the scene.
- **Paragraph uniformity:** AI prose clusters at 4–6 sentences per paragraph. Vary deliberately: include a one-line paragraph and a six-sentence one in every chapter.
- **Predictable arc:** every chapter should contain at least one moment the reader didn't see coming. Competent-but-predictable is still predictable.
- **Same ending as last chapter:** vary the closing register. Two emotional-pivot endings in a row read as formula.
- **Dialogue that sounds like prose:** real speech stumbles, interrupts, trails off, says the wrong thing. At least one imperfect line per scene.

## Anti-summarize rules (load-bearing)

The single most common failure mode is the model writing a **summary** of the chapter instead of the chapter. Both autonovel and authorclaw documented this bug. These rules exist because of it.

**Writer prompt must include:**
- "Write the COMPLETE chapter as actual prose, not a summary."
- "Do not write fewer than the target words. If running short, add more scenes, dialogue, internal monologue, sensory detail."
- "Do not truncate, summarize, or skip ahead."
- "Open with a hook — no throat-clearing. End with a reason to turn the page."

**Polish prompt must include:**
- "Produce a REVISED, POLISHED version of THE ENTIRE chapter."
- "Do NOT shorten the chapter. The polished version should be the same length or longer."
- "Do not output a list of changes or a critique."
- "Start directly with the chapter content. No preamble."

If the chapter comes back under target word count, that's a summary — regenerate, don't accept.

## Write → polish loop (per chapter)

1. **Write** the full draft against the assembled context window with the chapter-drafting directives above.
2. **Polish** in a separate pass — same persona, polish prompt above. Output replaces the draft.
3. Run `python scripts/slop_scan.py chapters/ch_NN.md`. Note the penalty.
4. Run the **LLM judge** (separate persona, harsh calibration). Score = judge_overall − slop_penalty.
5. **Stability-trap check:** does anything important **change** in this chapter? Is there a real cost? If not, flag for revision even if the score passes.
6. Score > 6.0 → keep:
   ```
   git add -A
   git commit -m "draft ch_NN: score X.XX (slop Y.Y) wc N"
   ```
   Else → discard and retry. After 5 attempts, keep the best attempt and flag the chapter for revision-phase attention.
7. **Canon/evidence extraction:** read the judge output for `new_canon_entries` (fiction) or `new_claims` (nonfiction). Append each to `canon.md` / `evidence.md` with source = `ch_NN`. The DB grows during drafting — this is how future chapters stay consistent.
8. Append `results.tsv`: `timestamp \t drafting \t ch_NN=X.XX \t <wc> \t keep|discard \t notes`.

## Continuity mechanisms (why chapters stay consistent)

Three reinforcing systems, all on:

1. **Canon/evidence DB** grows every chapter. The judge cross-references canon against each new chapter; a violation caps `canon_compliance` at 6.
2. **Context window** loads the previous chapter's tail (~2000 chars) and the next chapter's outline. You always know where you came from and where you're going.
3. **Foreshadowing/thread ledger** is checked at every chapter — plants and payoffs due this chapter are in the context, and the ledger is updated after.

## Post-draft sweep

After the last chapter:

1. Run `python scripts/slop_scan.py chapters/*.md` (full-manuscript sweep).
2. Look for **recurring** AI patterns across chapters — they compound. If "a sense of" appears in 12 chapters, that's a manuscript-level defect even if no single chapter crossed the threshold. Fix the worst offenders now.
3. Confirm the foreshadowing/thread ledger is fully resolved (every plant has a payoff or deliberate red herring).
4. Confirm `canon.md` / `evidence.md` is current.
5. Set `state.json.phase: revision`. Tell the user to run `/skill book-forge revision`.

## Common drafting failures (and fixes)

- **Under-length chapter (summary, not prose):** regenerate with stronger anti-summarize language; require ≥ target words.
- **No change in the chapter:** stability trap — rewrite forcing a real cost or irreversible decision.
- **Canon violation:** fix the chapter to match canon (almost always right), or, rarely, update canon if the chapter revealed a better choice and re-check downstream.
- **Banned-word hit:** the polish pass should have caught it; if it persists, manual edit.
- **Uniform sentence length:** ask the polish pass to deliberately vary length; re-run slop_scan.
