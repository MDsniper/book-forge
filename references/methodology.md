# Methodology

The conceptual heart of book-forge, ported from autonovel with additions from authorclaw. Read this before the first phase of any book.

## The five layers + one truth-DB

A book is six files that co-evolve. Order them abstract → concrete:

```
Layer 5: voice.md          — HOW we write (style, tone, vocabulary)
Layer 4: world.md          — WHAT exists (lore / domain map)
Layer 3: characters.md     — WHO acts (registry, arcs, relationships)
Layer 2: outline.md        — WHAT HAPPENS / WHAT'S ARGUED (beats + ledger)
Layer 1: chapters/ch_NN.md — THE ACTUAL PROSE
Cross-cutting: canon.md    — WHAT IS TRUE (hard facts / sourced claims)
```

Fiction and nonfiction map onto the same skeleton (see SKILL.md table). The layers are not a checklist — they are coupled. A change at any layer forces checks at adjacent layers.

### Propagation rules (who must be re-checked when X changes)

- `voice.md` changes → re-evaluate **all** chapters for adherence.
- `world.md` / `research-bible.md` changes → check every chapter for lore/claim consistency.
- `characters.md` changes → check arc consistency in `outline.md` and every chapter that character appears in.
- `outline.md` changes → check foreshadowing/thread ledger balance; check adjacent chapters.
- A chapter changes → check the foreshadowing/thread ledger and adjacent chapters.
- `canon.md` changes → check every chapter against the new/changed fact.

### Propagation debts

When writing reveals an upstream gap, log it in `state.json.debts`:

```json
{
  "trigger": "ch_07: magic system needs teleportation rules",
  "affected": ["world.md", "ch_03.md"],
  "status": "pending"
}
```

Process debts before declaring a phase complete. A debt's `status` moves `pending → in_progress → cleared`. A phase with open `pending` debts is not actually finished — surface them to the user before suggesting the next phase.

## The modify → evaluate → keep/discard loop

Every step inside every phase is the same loop:

1. **Generate** the artifact (or regenerate, targeting the weakest dimension).
2. **Evaluate** with the three immune systems (see `quality.md`).
3. **Decide:** improved → keep (git commit). Worse → discard.
   - Foundation & drafting: `git reset --hard HEAD~1`.
   - Revision (single chapter): revert only that chapter file (`git checkout HEAD -- chapters/ch_NN.md`) rather than rewinding the whole repo.
4. **Log** to `results.tsv`.

Git is the discard mechanism. This makes keep/discard a single command and gives you a complete audit trail. Every meaningful change gets a detailed commit message; the message is part of the audit log.

### Why "improved" and not "good enough"

Don't wait for "good enough" before keeping — that bar never arrives. Keep when this iteration is **better than the previous one** on the dimension you were targeting. The threshold gates (foundation ≥ 7.5, chapter > 6.0, plateau on revision) decide when to *leave the phase*, not when to keep an individual improvement.

## The anti-inflation principle

LLMs grade themselves generously. Every immune system is designed to fight this:

- **Mechanical slop** is objective — a banned word is a banned word regardless of how the model feels.
- **The LLM judge uses harsh calibration** (median = 6, 8 is exceptional, 10 "does not exist for a first draft") and a forced FINAL CHECK that *lowers* scores above 7 if the gap list reveals forced-invention problems.
- **The reader panel disagrees.** If four readers unanimously praise everything, they aren't reading carefully. Disagreement is signal.
- **Persona separation** — the writer never judges its own work in the same turn. Score what's on the page, not what you intended.

autonovel gets extra separation by using literally different models (Sonnet writes, Opus judges). A skill can't spawn a different model, so maximize what you can: harsh calibration, persona switching, parallel subagents for the panel, and — for the final dual-persona review — running it in a **fresh ZCode turn** with no conversation history of the writing.

## The stability trap

AI's worst narrative tendency is favoring stability over change — it reconciles, repairs, and resolves toward equilibrium. This is the opposite of what stories need (and what honest nonfiction needs, which is admitting when evidence is contested).

Countermeasures, enforced at every drafting and revision pass:

- Characters must end **truly different** — changed, damaged, or having chosen, not merely learned a lesson.
- Let bad things **stay bad**. Don't auto-repair damage by the next chapter.
- Allow irreversible decisions and real loss. Death is permanent; a betrayal cannot be unsaid.
- Withhold information from the reader (information economy). The reader should know less than the characters at some points, and more at others.
- Create genuine moral ambiguity. The right choice should cost something.
- Vary emotional intensity chapter to chapter. Two consecutive chapters at the same emotional pitch is a red flag.
- **If a choice has no real cost, it's not a real choice.**

Nonfiction variant: don't sand every claim into bland unanimity. Surface genuine scholarly debate, real tradeoffs, and where the evidence is uncertain or contested. A self-help book that pretends every technique works for everyone is dishonest.

## The three immune systems

(See `quality.md` for the verbatim rubric and lexicon.)

1. **Mechanical** — regex, no LLM. Detects banned words, AI-tell patterns, em-dash density, sentence-length uniformity, transition-opener ratio, show-don't-tell violations. Returns a 0–10 penalty subtracted from the judge score.
2. **LLM judge** — a separate persona scores on a fixed rubric (prose quality, voice adherence, beat/argument coverage, continuity, canon/evidence compliance, engagement) with harsh calibration and a forced FINAL CHECK.
3. **Reader/beta panel** — 4 personas read the whole book (or chapter) and report. Disagreements are where editorial decisions live. In revision, this is followed by a dual-persona review.

## Foreshadowing & thread ledgers (fiction)

`outline.md` carries a ledger table:

`| ID | Planted (ch) | Payoff (ch) | Thread | Status |`

Rules:
- Minimum one scene of separation between plant and payoff.
- **Rule of three** — important threads are referenced ~3 times before payoff.
- Every planted thread resolves or is a deliberate, explained red herring.
- Threads close in **reverse order of opening** (MICE quotient — like nested HTML tags). You can't close the outer thread before the inner one.

The foundation evaluator scores `foreshadowing_balance`; the full-book evaluator scores `foreshadowing_resolution`. A broken ledger is a structural defect.

Nonfiction uses an **argument/thread ledger** instead: every claim is planted, supported, and synthesized; nothing is dropped. The same reverse-closure logic applies to argument threads.

## What "done" means

- **Foundation done:** foundation_score ≥ 7.5 AND (lore_score ≥ 7.0 OR research_score ≥ 7.0), no pending debts, canon/evidence DB meets its target (fiction: 400+ entries; nonfiction: every claim sourced).
- **Drafting done:** every chapter at score > 6.0, full-manuscript slop sweep clean, canon/evidence current.
- **Revision done:** plateau reached (|Δ novel_score| < 0.3 after ≥ 3 cycles), dual-persona review stopping condition met.
- **Export done:** manuscript.md + at least one packaged format on disk.

"The reviewer always finds something." The stopping condition is about severity and qualification, not zero defects. When critique language shifts from "this has problems" to "these are the costs of the choice" — ship it.
