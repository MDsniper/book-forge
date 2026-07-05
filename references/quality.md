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

The judge is a **different persona** from the writer. Switch explicitly. The principle is industry-standard for AI evaluation: the writer never judges its own work, because self-evaluation drifts generous. We can't spawn a different model in a skill context, so the separation is enforced by persona switching + the harsh calibration below + the rule "score what's on the page, not what you intended." For maximum independence, the dual-persona review in revision can be run in a fresh ZCode turn with no prior conversation history.

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

LLM judges inflate. Fight it. Score against the bands below, and remember: a 7 is a chapter you'd be pleased to find in a published book. A 9 is something you'd quote. A 10 is reserved for work that did something you didn't think the medium could do. Almost nothing is a 10.

| Band | Meaning |
|---|---|
| **9.0–10.0** | Exceptional. You would save this chapter to reread. You can name the published books it belongs beside. Anything below genuine surprise is an 8 or lower. |
| **7.5–8.9** | Strong. Publishable with light edit. Zero major defects allowed here — even one structural problem caps the score at 7. |
| **6.0–7.4** | Solid. Functional, readable, but unremarkable. This is where most competent AI drafting lands. A perfectly acceptable floor for a first draft. |
| **4.0–5.9** | Underbuilt. The chapter works at the level of summary or sketch; a human writer would have to invent substantial material to make it real. |
| **Below 4.0** | Broken. Structural failure, incoherence, or generic to the point of being interchangeable with any other AI draft. |

The median for a competent AI-drafted chapter should sit around 6.0–6.5. Anything above 7 means the chapter did something most AI drafts don't. Anything above 8 means a human editor would keep it as-is. Treat 8+ scores with suspicion until you've found the gap you can't fix.

### Forced gaps (the engine of honesty)

Before scoring **any** dimension, the judge must name, in one or two sentences:
- The single weakest moment in that dimension (a quote, a scene, a beat).
- The specific change that would lift it.

If the judge can't find a weakness in a dimension, it must explain why — and the explanation must be specific, not "it's all good." Dimensions without an identified weakness are scored at 7 max. This is what prevents "everything is fine" outputs that defeat the whole loop.

### The forced re-read (apply to any score above 7)

After scoring, the judge re-reads its own gap list. If any gap names a problem that would force the writer to invent something mid-draft — a missing rule, an undefined character, a scene the outline promises but the foundation doesn't support — the score comes down. A book whose foundation forces invention under pressure is not a 7+. This is the single most important check; do not skip it.

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
