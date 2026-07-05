# Revision phase

The deep pass. This is where the book goes from "drafted" to "good." Run 3–6 cycles, stopping on plateau.

## Why revision is its own phase

Drafting optimizes for **forward progress** (a chapter at score > 6.0 is good enough to keep). Revision optimizes for **quality** across the whole manuscript. Different mindset, different tools, different stopping condition.

## The cycle

Each cycle:

1. **Adversarial cut analysis** (all chapters).
2. **Reader/beta panel** (whole book).
3. **Consensus items** → briefs.
4. **Brief → revision** per item, keep-if-improved-else-revert.
5. **Full-manuscript slop + judge** → novel_score.
6. **Plateau check.**

Then, after plateau: the **dual-persona review loop**.

## 1. Adversarial cut analysis

Persona: **ruthless editor.** "You cut fat from prose. You have no sentiment about good-enough sentences."

For each chapter, ask: **"If you had to cut 500 words from this chapter, what would you cut?"** What the editor would cut **is** the revision plan.

The editor quotes exactly and classifies each cut:
- **FAT** — wordy but not wrong.
- **REDUNDANT** — restates what the scene already showed.
- **OVER-EXPLAIN** — the narrator explains what the reader already understood. **This is the #1 AI pattern — expect ~30% of cuts here.**
- **GENERIC** — vague where it could be specific ("a bird" not "a jay").
- **TELL** — summarizes emotion the scene should show.
- **STRUCTURAL** — the scene doesn't earn its place.

Expected distribution: ~30% OVER-EXPLAIN, ~25% REDUNDANT, rest split among the others.

**Apply discipline:** analysis produces the cut list. A separate **apply** step executes the cuts mechanically. Don't conflate — analyzing and applying in the same pass leads to over-cutting.

Compression sweet spot: a revised chapter lands at **2200–3000 words**. Never go below **1800 words** — below that, the chapter becomes the new weakest link (over-compression is a real failure mode autonovel documented).

## 2. The reader/beta panel (4 personas)

Run as **parallel subagents** for genuine independence — each persona reads the manuscript fresh, without seeing the others' notes. The panel is the core quality signal.

### Fiction panel
- **The Editor** — prose texture, subtext, sentence craft. Cares about the line.
- **The Genre Reader** — reads 50+ books/year in this genre. Cares about pacing, mystery, payoff. Compares to the field's benchmarks (Sanderson, Le Guin, Jemisin for fantasy; Connell, Child for thriller; etc.).
- **The Writer** — has shipped novels. Cares about structure, beats, foreshadowing payoff. "I forgot I was reading" is the highest praise; "I can see the outline" is the worst.
- **The First Reader** — general reader. No craft terminology. Reports emotionally: "I had to put the book down," "I skimmed this part."

### Nonfiction panel
- **The Editor** — clarity, sentence craft, narrative flow.
- **The Subject Expert** — checks claims, evidence quality, and whether the book engages the field's real debates.
- **The Target Reader** — the person the book is for. Did they understand? Did it land? Was it useful?
- **The Skeptic** — actively argues against the thesis. Where does the book overreach? What's the steelman the book didn't engage?

### Self-help panel
- The four above, plus a **Sensitivity / claimer-of-authority** check: Is the book making promises it can't keep? Is it prescriptive where it should be suggestive? Does it acknowledge that techniques don't work for everyone?

**Disagreements between readers are where editorial decisions live.** If all four praise everything, re-run the panel — it didn't read carefully. The synthesis step doesn't average the panel; it surfaces the disagreements and decides.

## 3. Consensus → briefs

A revision item is a **consensus item** if ≥ 3 of 4 readers flagged it (or the same item surfaced in adversarial cut analysis AND ≥ 2 readers). Consensus items become revision priorities.

For each consensus item, write a **brief** (saved under `briefs/`):

```
PROBLEM:       <one sentence>
EVIDENCE:      <quotes from panel + cut analysis, with chapter refs>
WHAT TO KEEP:  <the good material in the scene that must survive>
TARGET:        <concrete outcome: cut to N words / add missing beat / dramatize / deepen>
```

Brief type maps to action:
- **CUT CANDIDATE** → compression brief. Target 40–60% cut, floor 1800w.
- **MISSING SCENE** → expansion brief. Keep the good material; add the missing beat.
- **THIN CHARACTER** → deepen an existing scene with an unguarded moment.
- **WEAK SCENE** → dramatization brief. Change HOW information arrives (e.g., reading-a-document → investigation/confrontation).
- **CONSISTENCY / TIMELINE** → fix in `canon.md` + all affected sources.
- **OVERREACH (nonfiction)** → soften the claim, add the steelman, or cut.

## 4. Brief → revision

For each brief:
1. Revise the chapter(s) against the brief. Same writer persona, same anti-summarize rules.
2. Re-evaluate: slop + judge on the revised chapter.
3. **Keep if `post_score >= pre_score`**, else revert (`git checkout HEAD -- chapters/ch_NN.md`).
4. Watch for **gen_revision over-generation** — the revision step tends to add ~30% more words than briefed. If the revised chapter balloons, trim back to target.

## 5. Full-manuscript score

After all consensus items in this cycle:
1. Run `python scripts/slop_scan.py chapters/*.md` (whole-book sweep).
2. Run the **full-novel judge** — scores prose quality, voice adherence, character/argument coherence, beat/coverage, continuity, canon/evidence compliance, engagement, **foreshadowing/thread resolution** (whole-book-only dimension).
3. `novel_score` = weighted sum − slop penalty.
4. `git commit -m "revision cycle N: novel_score X.XX"`.

## 6. Plateau detection

Stop cycling when **|`novel_score` − `prev_score`| < 0.3 after ≥ 3 cycles** (`MIN_REVISION_CYCLES = 3`, `MAX_REVISION_CYCLES = 6`, `PLATEAU_DELTA = 0.3`).

Also stop if you see the **whack-a-mole pattern**: raising one score drops another for two consecutive cycles. That's a structural ceiling — accept it. Pacing ~7 is a known LLM ceiling; chasing it past cycle 4 wastes effort.

## Apply vs. analyze discipline (critical)

authorclaw's deep revision is **21 steps** specifically because analysis and application are separated:

- **Analysis passes** (structural, scene-level, line-level, beta readers) produce *notes*.
- A **synthesis** step merges all notes into one action plan.
- **Apply passes** (3 of them) each take the prior output and rewrite the manuscript applying one layer of notes.

The bug this prevents: doing analysis and rewriting in the same pass leads to either shallow analysis (you start rewriting before you've finished reading) or chaotic rewriting (you change things as you notice them, losing coherence). **Always analyze fully first, then apply.** In book-forge's smaller scope: adversarial cut analysis + panel = analyze; brief → revision = apply.

## 7. The dual-persona review loop (after plateau)

The deepest pass. Send the **full manuscript** to a reviewer prompted:

> **Fiction:** "Read the below novel, '<title>'. Review it first as a literary critic (like a newspaper book review) and then as a professor of fiction. In the later review, give specific, actionable suggestions for any defects you find. Be fair but honest. You don't *have* to find defects."

> **Nonfiction:** "Read the below book, '<title>'. Review it first as a reviewer (like a major outlet's book review) and then as a subject-matter expert. In the later review, give specific, actionable suggestions for any defects, unsupported claims, or missing engagement with counterarguments. Be fair but honest."

Parse the review into items. Each item has:
- **severity:** major | moderate | minor
- **type:** prose | character | structure | claim | evidence | tone | other
- **qualified:** true if the language is hedged ("costs of ambition," "deliberate choice," "stylistic preference") vs. false if it's a flat defect

### Stopping conditions (any one)
- Stars ≥ 4.5 AND no major **unqualified** items.
- Stars ≥ 4 AND > 50% of items are **qualified**.
- ≤ 2 items found total.

Max 4 rounds. Each round: fix the top major-unqualified items, re-review. **"The reviewer always finds something — the stopping condition is about severity and qualification, not zero defects."** When the critique shifts from "this has problems" to "these are the costs of the choice," ship it.

For maximum reviewer independence, run the final review in a **fresh ZCode turn** with no prior conversation history.

## Exit criteria

- Plateau reached (or max cycles hit).
- Dual-persona review stopping condition met.
- Foreshadowing/thread ledger fully resolved.
- `canon.md` / `evidence.md` current; no fabricated citations.
- No pending propagation debts.

Then: set `state.json.phase: export`. Tell the user to run `/skill book-forge export`.
