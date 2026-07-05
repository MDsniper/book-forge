# Craft: plotting frameworks, beats, and ledgers

Reference for foundation and revision. Pick one primary framework per book and name it in `outline.md`. Hybrid frameworks are fine if you state the rule.

## Plotting frameworks (fiction)

### Save the Cat! (15 beats)
The default for commercial fiction. 15 beats mapped to chapter positions:

1. **Opening Image** (~1%) — the "before" snapshot.
2. **Theme Stated** (~5%) — someone says the theme, often obliquely.
3. **Set-Up** (1–10%) — protagonist's flawed world.
4. **Catalyst** (10%) — the inciting incident.
5. **Debate** (10–20%) — protagonist resists.
6. **Break into Two** (20%) — protagonist commits; Act 2 begins.
7. **B Story** (~22%) — the relationship/romance/mirroring subplot begins.
8. **Fun and Games** (20–50%) — the "promise of the premise"; the movie-poster scenes.
9. **Midpoint** (50%) — false victory or false defeat; stakes rise.
10. **Bad Guys Close In** (50–75%) — external + internal pressure compounds.
11. **All Is Lost** (75%) — the lowest point; whiff of death.
12. **Dark Night of the Soul** (75–80%) — protagonist processes.
13. **Break into Three** (80%) — the synthesis; Act 3 begins.
14. **Finale** (80–99%) — protagonist, changed, executes the new plan.
15. **Final Image** (~99%) — the "after" snapshot; mirrors #1.

### Dan Wells' 7-Point Story Structure
Good for tighter arcs: Hook → Plot Turn 1 → Pinch 1 → Midpoint → Pinch 2 → Plot Turn 2 → Resolution. Easier to map to short books and novellas.

### Story Circle (Dan Harmon)
8 steps in a circle: You (comfort) → Need → Go (enter unfamiliar) → Search (adapt) → Find (get what they wanted) → Take (pay the price) → Return (to familiar, changed) → Change. Strong for character-driven fiction and episodic structures.

### MICE quotient (Orson Scott Card)
Milieu, Idea, Character, Event — four story types. Threads open and close **in reverse order of opening** (like nested HTML tags). Use this to validate the foreshadowing ledger at foundation and again before export.

### Sanderson's Laws (magic systems)
- **1st Law:** An author's ability to solve conflict with magic is **directly proportional** to how well the reader understands that magic.
- **2nd Law:** Limitations > Powers. What the magic *can't* do is more dramatic than what it can.
- **3rd Law:** Expand on what you have before adding something new. One system with depth beats three with breadth.
- **0th Law:** Err on the side of awe over logic, but never break your own rules.

Apply at foundation: every magic system needs hard rules, costs, and societal implications. Without costs, there's no drama (Stability Trap).

### Scene-Sequel (Dwight Swain)
Alternating structure: **Scene** (Goal → Conflict → Disaster) followed by **Sequel** (Reaction → Dilemma → Decision). Pure scene is exhausting; pure sequel is static. The rhythm is the book's pulse.

## The foreshadowing ledger

Lives in `outline.md` Part 2. Format:

```markdown
| ID  | Planted (ch) | Payoff (ch) | Thread                          | Status     |
|-----|--------------|-------------|---------------------------------|------------|
| F01 | 3            | 17          | The broken compass points north | planted    |
| F02 | 5            | 12          | Mira's missing brother          | planted    |
| F03 | 7            | —           | The treaty's secret clause      | open       |
```

Rules:
- Minimum one scene of separation between plant and payoff.
- **Rule of three:** important threads referenced ~3 times before payoff.
- Every plant resolves or is a deliberate, explained red herring.
- **MICE closure:** threads close in reverse order of opening.
- Min 15 threads for a full novel (autonovel's floor). Plant-to-payoff distance ≥ 3 chapters.

Status values: `planted → referenced → resolved` (or `red-herring`).

The foundation judge scores `foreshadowing_balance`; the full-book judge scores `foreshadowing_resolution`. A broken ledger is a structural defect.

## Nonfiction equivalent: the argument/thread ledger

Same table structure, but the thread is a claim or argumentative thread, not a story plant:

```markdown
| ID  | Planted (ch) | Synthesis (ch) | Claim                                | Status     |
|-----|--------------|----------------|--------------------------------------|------------|
| A01 | 2            | 9              | Sleep affects decision quality       | supported  |
| A02 | 3            | 11             | The 10,000-hour rule has limits      | open       |
```

Every claim gets planted, supported with evidence (cross-ref `evidence.md`), and synthesized. Reverse-closure still applies: introduce sub-arguments before resolving the parent argument.

## Structural beat math

Implemented in `scripts/beat_math.py`. Given a chapter count, it prints the exact chapter each beat lands on. The defaults (Save the Cat! / standard commercial arc):

| Beat | Fraction | Default (22 ch) |
|---|---|---|
| Setup ends | × 0.12 | ch 3 |
| Inciting Incident | × 0.20 | ch 4–5 |
| Midpoint | × 0.50 | ch 11 |
| Twist / All Is Lost | × 0.75 | ch 16–17 |
| Climax | last 2 chapters | ch 21–22 |

If a beat lands between chapters, push it to the later chapter (better to enter a beat a touch late than early). If two beats land on the same chapter, you have a structural problem — merge or insert.

**Nonfiction argument arc** (used when book_type ∈ {nonfiction, self-help}):

| Beat | Fraction | Purpose |
|---|---|---|
| Setup | × 0.10 | Why this matters; the stakes |
| Problem | × 0.20 | The current state and what's wrong |
| Framework | × 0.35 | The mental model / lens the book offers |
| Evidence | × 0.65 | The case: data, cases, reasoning |
| Application | × 0.85 | What to do with it |
| Synthesis | last 1–2 ch | Tying it together; the steelman engaged |

`beat_math.py` supports both; pass `--mode fiction` (default) or `--mode nonfiction`.

## Scene-level beats (for outline detail)

When the outline is at scene-level (recommended for high-stakes chapters), each scene specifies:

- **POV** — whose head (fiction) or whose voice (nonfiction anecdote).
- **Goal** — what the POV character wants this scene.
- **Conflict** — what's in the way.
- **Outcome** — yes/no/yes-but/no-and. (Avoid pure "yes" — it kills tension.)
- **Emotional Arc** — start → end emotion (should change).
- **Plot Threads** — which ledger IDs touched this scene.
- **Word Count Target** — usually a fraction of the chapter target.

The Scene-Sequel rhythm governs how scenes chain: a high-conflict Scene should be followed by a reflective Sequel before the next Scene, especially in Act 2.

## Choosing a framework

- **Commercial fiction (fantasy, thriller, romance, sci-fi):** Save the Cat! as the spine, MICE for ledger validation, Sanderson for any magic.
- **Literary fiction:** Story Circle or 7-Point; lighter beat scaffolding, heavier character arc tracking.
- **Mystery/thriller:** Save the Cat! + a separate clue ledger (planted clues must equal or exceed what the detective uses to solve).
- **Nonfiction (narrative):** Argument arc beat math; use Scene-Sequel for any anecdote chapters.
- **Self-help:** Argument arc, with each Application chapter structured as Concept → Method → Example → Exercise.

State the framework choice in `outline.md` line 1 so every later phase knows the rules.
