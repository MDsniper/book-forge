# Collaborative mode (interview + checkpoints)

book-forge's default is autonomous — given an idea, it runs the whole pipeline hands-off. **Collaborative mode** adds back the human: a structured interview before foundation, plus three checkpoint reviews during foundation (and one at revision start). It's for authors who want the book to feel like *theirs*, not just an AI's interpretation of a one-line pitch.

`state.json.collaborative_mode ∈ {autonomous, collaborative}` records the choice per-book. Asked at seed time. Either mode still works on any book; the choice just routes the foundation phase.

This doc is the source of truth for both the interview and the checkpoints. Read it before running a collaborative foundation.

## When to use which

| You want... | Mode |
|---|---|
| Fastest path to a finished draft; you'll revise your voice in later | `autonomous` |
| The book to reflect your voice, themes, personal stake from page one | `collaborative` |
| Nonfiction/self-help/memoir with your anecdotes, opinions, examples | `collaborative` (strongly) |
| Fiction where you have a specific emotional core or theme in mind | `collaborative` |
| To just see what the AI does with a seed concept | `autonomous` |

## The interview (15 questions, ~10 minutes)

Conducted at seed time, after the user picks `collaborative` and before foundation begins. Ask all questions; let the user skip any. Capture every answer verbatim in `interview-answers.md` at the project root — these answers are load-bearing context for the foundation phase.

**Branching:** questions 1-5 are universal; 6-10 branch by `book_type`; 11-15 are universal.

### Universal (ask for every book)

1. **The hook, in your own words.** Beyond the one-line idea — what's the *feeling* you want a reader to walk away with? (One sentence is fine.)
2. **Target reader.** Not demographic — *who* are they, what's going on in their life when they pick this up? "A founder who just hit burnout," not "entrepreneurs."
3. **Three books you'd be proud to be shelved next to — and one you definitely wouldn't.** The "wouldn't" matters as much as the "would."
4. **Themes you care about.** What questions does this book sit with? Not answers — questions.
5. **Personal stake.** Why are *you* writing this? (For nonfiction/memoir: what experience or expertise are you drawing on? For fiction: what about this story hooks you specifically?)

### Fiction (6-10)

6. **Protagonist in one paragraph.** Who, what they want, what's in the way. It's fine if this is loose.
7. **The central tension you're drawn to.** What opposing forces create the engine? (Personal vs. cosmic, duty vs. desire, etc.)
8. **Tone and register.** Three adjectives for the prose you want. (Spare, cold, propulsive — or warm, lyrical, melancholy — anything.)
9. **Things you do NOT want.** Tropes, structures, character types, language — anything that would make you close the book.
10. **A scene or image that lives in your head for this book.** Even if it never makes the final cut, it tells us the visual/emotional world.

### Nonfiction (6-10)

6. **The single sentence this book argues.** Not the topic — the *claim*.
7. **The strongest version of the opposing view.** Who disagrees with you, and what's their best argument? (Steelman.)
8. **Three to five specific examples, anecdotes, or pieces of evidence you want included.** Yours, or from sources you trust. These will go into `evidence.md`.
9. **What would make this book *not* feel like yours?** Generic advice, hand-waving, particular phrases you avoid.
10. **What should the reader be able to *do* after reading?** For self-help especially — the concrete outcome.

### Universal (11-15)

11. **Pacing preference.** Slow-burn and atmospheric, or propulsive and page-turning, or mixed? (Mixed is the default.)
12. **Length target reality check.** The skill defaults to ~22 chapters × 3000 words (~66k). Want shorter/longer? Any hard ceiling?
13. **Series or standalone?** If series, do you have a sense of where this book sits in the arc?
14. **Anything from your life, your obsessions, your reading that you want woven in.** A specific craft, a region, a subculture, a piece of music, a hobby — concrete material that grounds the book in *you*.
15. **Open floor.** Anything else? Things you're worried about. Things you want to make sure the book does or doesn't do.

## How the answers get used

After the interview, before generating `world.md` / `research-bible.md` / `characters.md`:

- **`interview-answers.md`** at the project root captures every answer verbatim.
- **`voice.md` Part 2** (discovered voice) gets seeded from answers 3, 8/9, and 14 — the voice discovery sub-loop uses these as constraints, not just open exploration.
- **`world.md` / `research-bible.md`** gets seeded from answers 1, 4, 5, 10, 14.
- **`characters.md`** (fiction) gets seeded from answers 6, 7, 9.
- **`thesis.md`** (nonfiction) gets seeded from answers 6, 7, 10.
- **`evidence.md`** (nonfiction) gets pre-populated from answer 8.
- The foundation LLM judge's prompt gets a `## Author intent` section quoting answers 1, 3, 4, 5 verbatim. The judge scores against *your* intent, not just generic quality.

This isn't decorative — the answers change what gets generated. A book where the author said "I want spare, cold, propulsive prose, shelved next to Le Carré" produces a different foundation than "warm, lyrical, melancholy, shelved next to Le Guin."

## The three checkpoints (during foundation)

After the interview, foundation runs as usual — but pauses for your review at three moments. **Always pause; don't auto-advance.** Surface the artifacts clearly, ask the review question, wait for an answer, then proceed (or loop).

### Checkpoint 1 — after world / research bible (and characters if fiction)

Triggered when `world.md` (or `research-bible.md`) and `characters.md` first reach a passing score.

**What you show the user:**
- The full text of `world.md` / `research-bible.md` and `characters.md`.
- A short summary of how their interview answers were applied.

**The review question:**
> "Here's the world and cast, built from your interview answers. Read them and tell me: anything to change? Add? Cut? Anything that doesn't feel like the book you described? (Reply 'looks good' to continue, or give me notes.)"

**On feedback:** apply the changes directly to the docs, then re-show the changed sections. Loop until the user says "looks good" (or "continue"). Cap at 3 rounds — if they're still revising after that, suggest they edit the file by hand and run foundation again.

### Checkpoint 2 — after voice discovery

Triggered when the voice discovery sub-loop has written its 5 trial passages and selected a winner.

**What you show the user:**
- The 5 trial passages.
- The winner, with 2-3 exemplars and 2-3 anti-exemplars (as `voice.md` Part 2 would record them).
- The reasoning for the choice.

**The review question:**
> "Voice discovery picked [register X] based on match to your stated tone and the world. Look at the exemplars — does this feel right? Want a different register? Want to blend two? (Reply with the winner's letter, 'blend X+Y', or 'try again with different constraints'.)"

**On feedback:** if they pick a different register, regenerate Part 2 with that choice. If they want a blend, generate hybrid exemplars. Loop until satisfied. Cap at 2 rounds.

### Checkpoint 3 — after outline (the gate before drafting)

Triggered when `outline.md` (beats + foreshadowing/thread ledger) is complete and beat math has been validated.

**What you show the user:**
- The chapter-by-chapter beats.
- The foreshadowing/thread ledger.
- The structural beat map (Setup / Inciting / Midpoint / Twist / Climax positions).
- Total word-count estimate.

**The review question:**
> "Here's the structure. Read the beats — anything missing, anything in the wrong place, any thread you want planted or paid off differently? This is the last gate before drafting starts. (Reply 'looks good, draft' to begin drafting, or give me structural notes.)"

**On feedback:** apply structural changes; re-validate beat math and the ledger; re-show. This is the most important checkpoint — the outline is the contract the rest of the book executes against, so spend the time here. Cap at 4 rounds.

## The fourth checkpoint (revision start)

Triggered when the drafting phase completes and revision is about to start.

**What you show the user:**
- A one-paragraph-per-chapter summary (`arc_summary.md`).
- The full-manuscript slop score and the foundation-vs-final word count.
- The 3 lowest-scoring chapters with their judge notes.

**The review question:**
> "Drafting is done. Before revision starts: read the summaries. Anything you want to redirect — chapters you want restructured, scenes you want added/cut, characters you want deepened? Your notes here become the seed of the revision briefs. (Reply with notes, or 'revision can run autonomously'.)"

**On feedback:** the user's notes become *additional* consensus items for the revision briefs — they sit alongside the reader panel's findings and get priority weighting. Then revision runs as usual.

## How checkpoints interact with the loop

- **The keep/discard git loop stays intact.** Checkpoints are review moments between iterations, not interruptions of the loop.
- **If the user is unavailable** (e.g. they walked away and the skill is waiting), the skill should surface this clearly in its next message: "I paused at checkpoint 2 (voice). When you're ready, here's what I need from you."
- **If the user wants to bail on collaborative mid-book**, they can edit `state.json` to set `collaborative_mode: autonomous` and the remaining checkpoints become optional / skipped.

## What this mode does NOT do

- Does not pause per-chapter during drafting. Drafting is autonomous by design — forward progress over perfection. If you want per-chapter input during drafting, that's mode C (not implemented; would need a separate design).
- Does not let you write prose directly. The skill writes; you direct. If you want to write passages yourself, you can — paste them into the chapter file and the judge will treat them as canonical.
- Does not slow down the autonomous phases. Foundation-with-checkpoints takes ~longer than autonomous foundation, but drafting and revision run at the same speed either way.

## Reading the interview answers later

`interview-answers.md` is a permanent part of the book's project folder. It's useful:
- During revision, to re-check whether the book kept faith with your original intent.
- During the publish phase, when generating the blurb and metadata — the interview often contains better marketing language than the manuscript itself.
- For series planning, as the seed of the next book's interview.
