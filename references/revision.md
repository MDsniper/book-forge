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
Run as **parallel subagents** for genuine independence. Each reads the manuscript fresh, with no knowledge of the others' reactions. The disagreements are where the editorial decisions live.

- **The Line Editor** — reads for the sentence. Notices when prose goes slack, when rhythm flattens, when a metaphor is borrowed rather than made. Bored by cliché. Surprised by specificity. Cares about the line-by-line texture more than the plot.
- **The Genre Veteran** — has read widely and recently in this exact subgenre. Notices pacing problems, missed genre obligations (a romance without a black moment; a mystery that hides the clues), and payoffs that land flat because the setup was mishandled. Compares the book honestly against the field's recent best, not against a generic standard.
- **The Practitioner** — a working novelist reading as a craftsperson. Notices where structure shows through story ("I can see the outline"), where foreshadowing is too loud or too quiet, where a character arc bends without earning the bend. The highest praise is "I forgot I was reading"; the worst is "I see what you're trying to do."
- **The Stranger** — a thoughtful general reader with no craft vocabulary. Reports experience, not analysis: where they put the book down to do something else, where they read a passage twice, where they were confused, where they would tell a friend about it. Their confusion and boredom are the most honest signals you'll get.

### Nonfiction panel
- **The Line Editor** — clarity at the sentence level, narrative flow across paragraphs, and whether the prose earns the reader's attention.
- **The Subject Expert** — a working specialist in the book's field. Checks claims against the evidence, identifies overreach, and asks whether the book engages the field's actual debates or strawmans them.
- **The Target Reader** — the person the book is for, not a general reader. Did the promise land? Was the method clear? Were the examples useful? Would they recommend it to someone with the same problem?
- **The Skeptic** — actively argues against the thesis. Where does the book reach past its evidence? What's the strongest version of the opposing view, and does the book engage it or sidestep it?

### Self-help panel
The nonfiction panel, plus a **claimer-of-authority check**: Is the book promising more than the evidence supports? Is it prescriptive where it should be suggestive? Does it acknowledge that no technique works for everyone, and tell the reader what to do if it doesn't work for them?

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

The deepest pass. Send the **full manuscript** to a reviewer prompted in two passes — first as a critic writing for an audience, then as a craftsperson writing for the author. The first pass is about whether the book works; the second is about how to fix what doesn't.

> **Fiction review prompt:** "Read the manuscript of '<title>'. First, write the review a working literary critic would publish in a serious outlet — fair, specific, neither damning with faint praise nor gushing. Then, switching to the perspective of an experienced fiction writer who has been paid to teach the craft, give the author concrete, prioritized notes on what to fix. Note any genuine defects: scenes that sag, characters who flatten, prose that drifts, structure that telegraphs. Also note where the book succeeds — solutions matter as much as problems. You are not required to find problems that aren't there; honest praise is part of the job."

> **Nonfiction review prompt:** "Read the manuscript of '<title>'. First, write the review a critic at a major outlet would publish — engaging with the thesis, the evidence, and the book's contribution. Then, switching to the perspective of a subject-matter expert who has peer-reviewed work in this field, give the author concrete notes: unsupported claims, overreach, missing engagement with counterarguments, weak sourcing, or unclear reasoning. Flag what works as well as what doesn't."

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
