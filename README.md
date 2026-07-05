# book-forge

An autonomous book-writing skill. Plans, writes, revises, and exports full-length books — **fiction, nonfiction, and self-help** — from a one-line idea to a packaged manuscript.

Inspired by the methodology of [autonovel](https://github.com/NousResearch/autonovel) (NousResearch) and the workflow design of [authorclaw](https://github.com/Ckokoski/authorclaw) (Ckokoski, MIT licensed). All expression in this skill is original — see [Credits](#inspiration--credits) and [NOTICE](./NOTICE) for details.

## Works in: ZCode · Claude Code · Factory Droid · OpenCode · Kimi CLI · OpenClaw · Hermes Agent

This skill follows the **Agent Skills standard** (`SKILL.md` + YAML frontmatter + bundled `scripts/`/`references/`/`assets/`), so the same files work across all seven agents. It's installed at:

| Agent | Path |
|---|---|
| ZCode | `~/.agents/skills/book-forge/` |
| Claude Code | `~/.claude/skills/book-forge/` |
| Factory Droid | `~/.factory/skills/book-forge/` |
| OpenCode | `~/.config/opencode/skills/book-forge/` |
| Kimi CLI | `~/.kimi/skills/book-forge/` |
| OpenClaw | `~/.openclaw/skills/book-forge/` |
| Hermes Agent | `~/.hermes/skills/writing/book-forge/` |

(OpenCode and Kimi also discover `~/.agents/skills/` directly, so the ZCode copy is visible to them too. Hermes organizes skills by category, hence the `writing/` subdir. OpenClaw's `~/.openclaw/skills/` is the user-skills root; built-in skills live under `~/.openclaw/install/skills/`.)

## Quick start

```bash
mkdir ~/Documents/MyBook && cd ~/Documents/MyBook
```

Then invoke in your agent of choice (each phase is one invocation):

| Phase | Claude Code / Factory Droid / ZCode | OpenCode | Kimi CLI | OpenClaw / Hermes |
|---|---|---|---|---|
| seed (start) | `/book-forge` | "use the book-forge skill to start a book" | `/skill:book-forge` | "use the book-forge skill to start a book" |
| foundation | `/book-forge foundation` | "continue book-forge foundation phase" | `/skill:book-forge foundation` | "run book-forge foundation phase" |
| drafting | `/book-forge drafting` | "run book-forge drafting" | `/skill:book-forge drafting` | "run book-forge drafting phase" |
| revision | `/book-forge revision` | "run book-forge revision" | `/skill:book-forge revision` | "run book-forge revision phase" |
| export | `/book-forge export` | "run book-forge export" | `/skill:book-forge export` | "run book-forge export phase" |

- **Claude Code / Factory Droid / ZCode:** slash command `/book-forge <phase>`. Auto-triggers from the description if you just say "write a book."
- **OpenCode:** no slash command for skills — the agent auto-loads it via the `skill` tool, or you can prompt it explicitly.
- **Kimi CLI:** `/skill:book-forge <phase>` (note the colon).
- **OpenClaw:** auto-loads from `~/.openclaw/skills/`; invoke from any channel (chat, CLI `openclaw agent`, Control UI) by saying "use the book-forge skill." Scripts run via the `exec` tool (make sure `exec` is in your `tools` allowlist if you set one).
- **Hermes Agent:** auto-loads from `~/.hermes/skills/writing/`; invoke by saying "use the book-forge skill."
- All agents: one phase per invocation, then return control.

## Keeping them in sync

The seven copies are independent. To re-sync after editing the canonical copy at `~/.agents/skills/book-forge/`:

```bash
SRC=~/.agents/skills/book-forge
for dest in ~/.claude/skills ~/.factory/skills ~/.config/opencode/skills \
            ~/.kimi/skills ~/.openclaw/skills ~/.hermes/skills/writing; do
  rm -rf "$dest/book-forge" && cp -R "$SRC" "$dest/book-forge"
done
```

## The model in one breath

A book is **five co-evolving layers + one truth-DB**:

| Layer | Fiction | Nonfiction / Self-help |
|---|---|---|
| `voice.md` | prose style | author voice |
| `world.md` | lore, magic, geography | domain map, terminology |
| `characters.md` | registry, arcs | personas, case figures |
| `outline.md` | beats + foreshadowing ledger | chapter list + thread ledger |
| `chapters/ch_NN.md` | the prose | the prose |
| `canon.md` | hard-facts DB | **claims/evidence DB** (no fabricated citations) |

Every phase is a **modify → evaluate → keep/discard loop**, with git commits as keeps and `git reset --hard HEAD~1` as discards. Three quality "immune systems" run on every chapter and on the full manuscript:

1. **Mechanical slop** — `scripts/slop_scan.py` (regex, no LLM).
2. **LLM judge** — a separate persona with harsh anti-inflation calibration.
3. **Reader/beta panel** — 4 personas run as parallel subagents; disagreements are where editorial decisions live. Followed by a dual-persona final review.

## Book types

`state.json.book_type ∈ {fiction, nonfiction, self-help}` routes foundation and revision:

- **fiction** → world-building + 400+ canon entries + foreshadowing ledger (MICE closure) + 4-persona reader panel.
- **nonfiction** → research bible + every claim sourced + argument/thread ledger + fact-check + Skeptic panelist.
- **self-help** → as nonfiction, plus Concept→Method→Example→Exercise structure + sensitivity/claimer-of-authority check.

## Dependencies

- **Always required:** `git`, `python3` (you have both).
- **For EPUB/DOCX:** `pandoc` — `brew install pandoc`.
- **For PDF:** a LaTeX engine — `brew install --cask mactex` (full) or `cargo install tectonic` (lightweight).
- **Optional:** `epubcheck` — `brew install epubcheck` (validates EPUB output).

Export never fails because a tool is missing — it produces what it can and prints the install hint.

## Files in this skill

```
book-forge/
├── SKILL.md                  orchestration brain (read this first)
├── README.md                 this file
├── references/               load on demand (see SKILL.md for routing)
│   ├── methodology.md        5-layer+canon model, the loop, stability trap
│   ├── foundation.md         phase 1 procedure + scoring + voice discovery
│   ├── drafting.md           phase 2 + the 24 writing instructions + anti-summarize
│   ├── revision.md           phase 3 + adversarial cut analysis + panel + review
│   ├── quality.md            the three immune systems verbatim
│   ├── craft.md              plotting frameworks, foreshadowing ledger, beat math
│   ├── nonfiction.md         nonfiction & self-help adaptation
│   ├── export.md             packaging + front/back matter + KDP readiness
│   └── genres.md             per-genre voice/structure/benchmarks
├── assets/
│   ├── templates/            state.json, project.yaml, world.md, characters.md,
│   │                         outline.md, canon.md, evidence.md, voice.md,
│   │                         MYSTERY.md, thesis.md, research-bible.md, seed.txt
│   ├── banned-words.txt      slop lexicon (Tier 1 + 3)
│   └── ai-tells.txt          regex patterns for AI fiction tells
└── scripts/
    ├── slop_scan.py          mechanical slop scanner (0-10 penalty)
    ├── beat_math.py          structural-beat calculator
    ├── assemble.py           chapters/ → manuscript.md, rebuild outline/arc
    └── export.py             pandoc EPUB/DOCX + LaTeX PDF
```

## Per-book structure (created by the seed phase)

```
MyBook/
├── .book-forge/
│   ├── banned-words.txt      project-specific slop overrides (optional)
│   └── ai-tells.txt          project-specific tell overrides (optional)
├── seed.txt
├── state.json                master phase tracker
├── project.yaml              metadata
├── voice.md, world.md (or research-bible.md), characters.md
├── outline.md (with ledger), canon.md (or evidence.md)
├── MYSTERY.md (fiction) / thesis.md (nonfiction)
├── chapters/
│   └── ch_01.md ... ch_NN.md
├── briefs/                   revision briefs
├── manuscript.md             assembled (after export)
├── front-matter.md, back-matter.md
├── results.tsv               audit log (every keep/discard)
└── exports/                  final EPUB / DOCX / PDF
```

## Inspiration & credits

book-forge is an original work that draws inspiration from two projects in the AI-book-writing space. All expression in this skill (prompts, lexicons, prose, code) is original to book-forge.

- **[authorclaw](https://github.com/Ckokoski/authorclaw)** (© 2026 Writing Secrets / Beach Blogger LLC, MIT licensed) — portions of this skill adapt ideas from authorclaw, including the write→polish two-step with anti-summarize output rules, the analyze-vs-apply revision discipline, structural beat math, and the no-fabricated-citations hard rule. The MIT license and copyright notice are preserved in [NOTICE](./NOTICE). Per the MIT license, this attribution is provided in derivative work; authorclaw's authors do not endorse this project.

- **[autonovel](https://github.com/NousResearch/autonovel)** (NousResearch) — autonovel's *methodology* (the 5-layer + canon model, the modify-evaluate-keep/discard loop, the use of multiple "immune systems" for quality control, the foreshadowing ledger, the anti-inflation principle) inspired the design of this skill. **No source code or text from autonovel is included.** At the time of this release, autonovel does not carry a license file; we therefore limited our reuse to the ideas and methodology (which are not copyrightable) and wrote all expression from scratch. If autonovel's maintainers add a permissive license, we would welcome the opportunity to credit them more formally.

The book-writing methodology this skill implements (Save the Cat, Story Circle, MICE quotient, Sanderson's Laws, foreshadowing ledgers, scene-sequel structure) predates both projects and is drawn from the open craft literature (Snyder, Harmon, Card, Sanderson, Swain, Weiland, etc.).

## License

MIT.
