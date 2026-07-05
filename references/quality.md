# Quality: the three immune systems

Always on, every phase. These are what separate a book-forge manuscript from a raw LLM dump.

## Immune System 1 — Mechanical slop (regex, no LLM)

Implemented in `scripts/slop_scan.py`. Reads lexicons from `assets/banned-words.txt` and `assets/ai-tells.txt`. Returns a 0–10 penalty subtracted from the judge score.

### Tiers

**Tier 1 — banned words (single-word hits):** corporate-AI vocabulary that almost never appears in good prose. Examples: delve, utilize, leverage, tapestry, paradigm, myriad, plethora, robust, seamless, intricate, nuanced (when overused), realm, journey (as metaphor), resonate, elevate, empower, foster, navigate (as metaphor), landscape (as metaphor). The full list is in `assets/banned-words.txt`; add project-specific bans to the project's `.book-forge/banned-words.txt`.

**Tier 2 — cluster detection:** when ≥ 3 Tier-1 words appear within 500 words, escalate the penalty (clustered slop is worse than isolated).

**Tier 3 — filler phrases:** "in today's fast-paced world," "at the end of the day," "it's important to note that," "plays a crucial role," "a testament to," "in the realm of." Each hit adds to the penalty.

### Fiction-specific AI tells (regex)

From `assets/ai-tells.txt`. These are patterns that scream LLM fiction:
- `a sense of \w+` ("a sense of dread," "a sense of belonging")
- `couldn't help but feel`
- `the weight of \w+` ("the weight of responsibility")
- `eyes widened` / `eyes narrowed` (overused)
- `heart pounded in (?:his|her|their) chest`
- `(?:raven|dark|golden|silken) hair (?:spilled|cascaded|framed)`
- `a shiver ran down (?:her|his|their) spine`
- `not just X, but Y` (overused construction)
- `there's a difference between X and Y`
- `something shifted between them`
- `the air hung heavy`
- em-dash density > 15 per 1000 words

### Structural tics
- **Sentence-length CV (coefficient of variation) < 0.3** → uniform sentence length, penalized. Good prose varies.
- **Transition-opener ratio > 0.3** → too many paragraphs opening with "However," "Moreover," "Meanwhile," "Suddenly." Penalized.
- **Show-don't-tell patterns:** "She felt X," "He was Y," "She knew that" — counted; high density penalized.

### Composite penalty

The script sums hits across tiers and normalizes to 0–10. A clean chapter is 0–1; a typical AI first draft is 3–5; a slop-heavy draft is 7+. The penalty is **subtracted from the judge's overall score**, so a slop-penalty of 4 on a judge-score of 7 yields a final of 3 — below the chapter threshold of 6, forcing regeneration.

Run on every chapter after polish, and on the full manuscript after the draft sweep.

## Immune System 2 — LLM judge (separate persona)

The judge is a **different persona** from the writer. Switch explicitly. The principle from autonovel: *"Different judge: Evaluation model should differ from writing model when possible to avoid self-congratulation bias."* We can't spawn a different model, so the separation is enforced by persona switching + harsh calibration + "score what's on the page, not what you intended."

### Judge system prompt

> "You are a literary critic and novel editor. You evaluate fiction with precision. You score what is on the page, not what the writer intended. Always respond with valid JSON. No markdown fences, no preamble — just the JSON object."

Nonfiction variant: "You are an editor and fact-checker for a major publisher. You evaluate nonfiction with precision..."

### Scoring dimensions

Fiction chapter:
- `prose_quality` (0–10)
- `voice_adherence` (0–10)
- `character_voice` (0–10)
- `beat_coverage` (0–10) — did it hit the outline beats?
- `plants_seeded` (0–10) — foreshadowing due this chapter actually planted?
- `continuity` (0–10) — consistent with previous chapter + canon?
- `canon_compliance` (0–10) — capped at 6 if a canon violation is found
- `lore_integration` (0–10)
- `engagement` (0–10)

Full-novel adds: `foreshadowing_resolution`, `pacing`, `thematic_coherence`.

Nonfiction chapter: `clarity`, `voice_adherence`, `claim_support` (capped at 6 if a claim lacks a source), `structure`, `engagement`, `audience_fit`.

### Harsh calibration (the anti-inflation core)

> **9–10:** Could not improve this with a month of focused editorial work. Reserve 10 for work that **surprises** you.
> **7–8:** Strong. A score of 8+ requires **zero major gaps**.
> **5–6:** Competent but unremarkable. The median AI output.
> **Below 5:** Real problems.

### FINAL CHECK (always apply)

> If your overall_score is above 7, re-read your gap lists. If any gap describes a problem that would force a writer to stop and invent something during drafting, your score is too high. Revise down.

### Forced gaps

For **every** dimension, the judge must identify the weakest moment in the chapter and a concrete fix. No dimension gets a free pass. This is what prevents "everything is fine" outputs.

### Output format (JSON, no fences)

```json
{
  "overall_score": 6.2,
  "dimensions": {
    "prose_quality": {"score": 6, "weakest_moment": "<quote>", "fix": "<concrete>"},
    ...
  },
  "new_canon_entries": [
    {"fact": "...", "source": "ch_07"},
    ...
  ],
  "summary": "<2-3 sentence honest assessment>"
}
```

## Immune System 3 — Reader/beta panel + dual-persona review

See `revision.md` for the full procedure. Summary:

- **4-persona panel** runs as **parallel subagents** for genuine independence. Disagreements are where editorial decisions live. If all four agree on everything, re-run — it didn't read carefully.
- **Dual-persona review** (post-plateau): full manuscript reviewed first as a critic/reviewer, then as a professor/subject-expert. Parse items with severity and qualification; stop on severity/qualification, not zero defects.

## Specificity kills slop

The single best anti-slop technique, applicable everywhere:

- "a bird" → "a jay"
- "a metallic scent" → "the smell of hot iron"
- "she was angry" → "she set the cup down too hard; tea slopped"
- "the city" → "the stair-streets of Upper Halberd"
- "many people" → "forty-three people" (if you know) or "the crowd" (if you don't)

Vague is the AI signature. Specificity is the cure. The slop scanner can't catch vagueness directly (it's not a regex), so the judge and panel must flag it under `prose_quality`.

## Earn every metaphor

Metaphors come from the character's domain, not from a generic literary stockpile:
- A blacksmith → heat, metal, hammer-rhythm.
- A sailor → tides, line tension, weather.
- An accountant → ledgers, reconciliation, compound interest.
- A self-help writer → the actual concrete situations of the reader, not "climbing your personal mountain."

Stock metaphors ("a tapestry of," "navigating the labyrinth of," "the weight of") are slop. The banned-words list catches the worst; the judge catches the rest.
