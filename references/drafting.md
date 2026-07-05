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

## The 24 writing instructions

Read these into the writer persona before every draft. They are the difference between a chapter and a summary.

**Target & shape**
1. Write approximately the target word count (default 3000). Do not truncate.
2. Third-person limited past tense, locked to one POV character (fiction). Nonfiction: stay in the chosen register from `voice.md` Part 2.
3. Hit all beats in this chapter's outline.
4. Plant every foreshadowing item due this chapter; pay off every item due.

**Texture**
5. Sensory detail in every scene — at least three senses.
6. No words from the banned list (`assets/banned-words.txt` + project overrides).
7. No AI fiction tells (`assets/ai-tells.txt`).
8. Vary sentence length. Long, medium, short. Sentence-length CV should be ≥ 0.3.
9. Metaphors come from the character's experience (blacksmith → heat/metal; sailor → tides). For nonfiction, metaphors from the subject domain.
10. Trust the reader. Don't over-explain.
11. Show, never tell emotions. (Fiction.)

**Structure**
12. Start **in scene**. No throat-clearing, no weather, no waking up unless it's load-bearing.
13. End on a moment — a turn, an image, a question — not a summary.

**Anti-patterns (items 14–24)**
14. No triadic lists ("X, Y, and Z") more than once per chapter.
15. No "He did not [verb]" constructions more than once.
16. No "He thought about [X]" more than once — dramatize the thought instead.
17. No "the way [X] did [Y]" more than twice.
18. No over-explaining after showing. Once you've shown it, move on.
19. Max 2 section breaks per chapter.
20. Vary paragraph length. Avoid a run of same-length paragraphs.
21. End differently from the previous chapter. Vary the closing register.
22. Include at least one **surprising moment** — something the reader didn't predict.
23. ≥ 70% of the chapter in-scene (dialogue + action), ≤ 30% summary/reflection.
24. Dialogue sounds like speech, not like exposition with quotation marks. People interrupt, deflect, and don't finish sentences.

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

1. **Write** the full draft against the assembled context window with the 24 instructions.
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
