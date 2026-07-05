# Nonfiction & self-help adaptation

The same engine, routed by `book_type ∈ {nonfiction, self-help}`. The 5-layer + canon model is general; this doc specifies how it bends.

## The core difference

Fiction's substrate is **a world that must be internally consistent** (canon = what's true in the world). Nonfiction's substrate is **a thesis that must be externally defensible** (canon = what's true in the real world, with sources). Everything downstream follows from that.

- **Canon → Evidence DB.** Every claim sourced. No fabricated citations. Ever.
- **World → Research bible.** Topic, audience, thesis, terminology, contested questions.
- **Characters → Figures / personas.** Case-study subjects, exemplar personas, or (self-help) reader archetypes.
- **Outline beats → Argument arc.** Setup → Problem → Framework → Evidence → Application → Synthesis.
- **Foreshadowing ledger → Argument/thread ledger.** Every claim planted, supported, synthesized; nothing dropped.
- **MYSTERY.md → thesis.md.** The single sentence the book argues, plus the **steelman** (strongest opposing view). The book must engage the steelman, not strawman it.

## Foundation (nonfiction)

Replaces world-building with **research**. Procedure:

1. **`research-bible.md`:**
   - **Topic & scope** — what the book covers and (importantly) what it doesn't.
   - **Target reader** — concretely. "Mid-career engineers moving into management," not "professionals."
   - **Core thesis** — one sentence. (Must match `thesis.md`.)
   - **Key terminology** — defined, consistent, with preferred terms and terms-to-avoid.
   - **The field's contested questions** — where reasonable people disagree. The book must engage these, not pretend they don't exist.

2. **`thesis.md`:** the single-sentence thesis, the steelman of the opposing view, and 3–5 supporting sub-claims that structure the book.

3. **`evidence.md` (the canon equivalent):** every claim the book will make, each with:
   - The claim (falsifiable).
   - A **real, verifiable source.** (No fabrication. If unverifiable: `unverified`.)
   - The source type (peer-reviewed / journalistic / expert opinion / anecdotal / author's original analysis).
   - A confidence level (high / medium / low).
   - **Target: every chapter's claims sourced before drafting begins.** Unlike fiction's 400-entry target, the bar here is *coverage* — no claim goes to draft without a source.

4. **`outline.md`** on the argument arc (see `craft.md` nonfiction beat math). Each chapter specifies which claims it advances.

5. **Voice discovery sub-loop** in nonfiction registers: authoritative, confessional, coach, lyrical, reportorial. Pick the one that fits the audience.

6. **Cross-layer checks:** every outline claim exists in `evidence.md`; the steelman is engaged somewhere in the arc; terminology is consistent.

7. **Foundation judge (nonfiction weighting):** Research/thesis 40%, Structure 25%, Audience-fit 20%, Voice 15%. Gate: `research_score ≥ 7.0`.

## Self-help specifics

Self-help is nonfiction with a prescriptive spine. Add:

- **A methods chapter early** — the reader needs the lens before the advice.
- **Concept → Method → Example → Exercise** structure in Application chapters.
- **Honesty about limitations** — a self-help book that promises its technique works for everyone is lying. Each method chapter should state who it works for, who it doesn't, and what to do if it doesn't work for you.
- **The claimer-of-authority check** (in revision): is the book promising more than the evidence supports? "May help with" vs. "cures." Prescriptive where it should be suggestive is a real failure mode.

## Drafting (nonfiction)

Same write→polish loop, same context window, same 24 instructions (with fiction-only items 11 and 23 relaxed). Additions:

- **Every claim must trace to `evidence.md`.** The judge's `claim_support` dimension is capped at 6 if any claim lacks a source. The writer persona instruction: "If you make a claim, it must have a source in `evidence.md`. If you can't find one, mark the claim `[NEEDS SOURCE]` and continue — do not fabricate."
- **The steelman must appear.** Somewhere in the relevant chapter, engage the strongest opposing view honestly. Don't strawman.
- **Hedging language** is appropriate ("the evidence suggests," "in most studies," "for many people"). Don't overclaim. Don't underclaim either — weak claims are boring.
- **Anecdotes are flagged as anecdotes.** A case study is illustrative, not proof. Mark which is which.

## The `[NEEDS SOURCE]` workflow

During drafting, the writer may produce a claim that isn't in `evidence.md`. Rather than fabricate, it writes `[NEEDS SOURCE: <claim>]` inline. After the draft:

1. Collect every `[NEEDS SOURCE]` tag.
2. For each, either (a) find a real source via web search (verify it — read the actual source, don't trust a snippet), or (b) cut/soften the claim if no source exists.
3. Add resolved sources to `evidence.md`.
4. Remove the tag.

A claim that survives to export with `[NEEDS SOURCE]` still in it is a **hard failure** — export must refuse. This matches authorclaw's no-fabrication rule.

## Revision (nonfiction)

The reader panel becomes **Editor / Subject Expert / Target Reader / Skeptic** (self-help adds the Sensitivity/claimer-of-authority check). Add:

- **Fact-check pass** — the Subject Expert verifies every claim against its cited source. Common failure: the source says something more nuanced than the book claims (overclaiming). Fix by softening.
- **Steelman audit** — did the book actually engage the strongest opposing view, or a weak one? If weak, strengthen the engagement.
- **Currency check** — are the sources recent enough for the field? (Medicine, tech: very recent. History: older is fine.)
- **Anecdote honesty** — are anecdotes presented as proof when they're illustration? Fix the framing.

The dual-persona review prompt (see `revision.md`) uses the nonfiction variant: reviewer then subject-matter expert.

## Common nonfiction failure modes

- **Overclaiming** — "X causes Y" when the evidence shows correlation. Fix: "X is associated with Y; the causal direction is debated."
- **Cherry-picking** — citing only supportive sources. Fix: cite the meta-analysis or the strongest counter-source.
- **Strawman** — engaging a weak version of the opposing view. Fix: use the steelman from `thesis.md`.
- **Vague audience** — "for everyone." Fix: name the reader concretely in `research-bible.md`.
- **Method-as-panacea (self-help)** — promising universal results. Fix: state limitations explicitly.
- **Fabricated citation** — inventing a source. **Hard failure.** Fix: find a real source or cut the claim.

## Export considerations

- Front matter must include a **sources/bibliography** section built from `evidence.md`.
- Self-help: appendices with exercises, worksheets, and "if this didn't work for you" pointers.
- Nonfiction narrative: endnotes (academic) or bibliography (trade), depending on audience.

The export script builds the bibliography automatically from `evidence.md` — every cited source appears, deduplicated.
