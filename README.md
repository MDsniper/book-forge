# book-forge

An autonomous book-writing skill for AI coding agents. **Plans, writes, revises, exports, publishes, and markets** full-length fiction, nonfiction, and self-help books — from a one-line idea to a packaged manuscript ready for KDP, plus cover art and a 90-day launch marketing kit.

Inspired by the methodology of [autonovel](https://github.com/NousResearch/autonovel) (NousResearch) and the workflow design of [authorclaw](https://github.com/Ckokoski/authorclaw) (Ckokoski, MIT licensed). All expression in this skill is original — see [Credits](#inspiration--credits) and [NOTICE](./NOTICE) for details.

## What book-forge does

Six phases, each one invocation of the skill. You steer between phases.

| Phase | What it produces |
|---|---|
| **seed** | `seed.txt`, `project.yaml`, `state.json`, all templates copied, `git init`, optional 15-question interview (collaborative mode) |
| **foundation** | `world.md`/`research-bible.md`, `characters.md`/`thesis.md`, `outline.md` (with foreshadowing/thread ledger), `voice.md` Part 2, `canon.md`/`evidence.md`, `MYSTERY.md` (fiction) |
| **drafting** | `chapters/ch_NN.md` — write→polish loop with slop detection + judge evaluation |
| **revision** | Adversarial cut analysis, 4-persona reader panel, brief→revise, dual-persona final review |
| **export** | `manuscript.md` + EPUB + DOCX + PDF via pandoc + LaTeX |
| **publish** | Real copyright page, ISBN-stamped KDP/Ingram metadata, pricing math, cover spec, legal disclaimers, marketing bundle (blurb/ad copy/social/ARC email), 90-day launch timeline |

Five quality "immune systems" run on every chapter: mechanical slop scanner, LLM judge with harsh calibration, reader panel, dual-persona review, and stability-trap countermeasures (forced character change, irreversible loss, information economy, genuine moral cost).

Plus a **provider-agnostic image generator** (`scripts/image.py`) for covers and interior illustrations — supports ComfyUI (free/self-hosted), Google Imagen, OpenAI gpt-image-1, fal.ai, Ideogram, Stability, Replicate.

## Works in 7 agents

The skill follows the **Agent Skills standard** (`SKILL.md` + YAML frontmatter + bundled `scripts/`/`references/`/`assets/`), so the same files work across all seven:

| Agent | Path |
|---|---|
| ZCode | `~/.agents/skills/book-forge/` |
| Claude Code | `~/.claude/skills/book-forge/` |
| Factory Droid | `~/.factory/skills/book-forge/` |
| OpenCode | `~/.config/opencode/skills/book-forge/` |
| Kimi CLI | `~/.kimi/skills/book-forge/` |
| OpenClaw | `~/.openclaw/skills/book-forge/` |
| Hermes Agent | `~/.hermes/skills/writing/book-forge/` |

OpenCode and Kimi also discover `~/.agents/skills/` directly. Hermes organizes skills by category (hence the `writing/` subdir). OpenClaw's `~/.openclaw/skills/` is the user-skills root; built-in skills live under `~/.openclaw/install/skills/`.

## Quick start

```bash
mkdir ~/Documents/MyBook && cd ~/Documents/MyBook
```

Then invoke in your agent:

| Agent | How |
|---|---|
| Claude Code / Factory Droid / ZCode | `/book-forge <phase>` |
| Kimi CLI | `/skill:book-forge <phase>` |
| OpenCode / OpenClaw / Hermes | describe what you want — "use the book-forge skill to start a book" |

**Working npx invocation** (for when you're starting from outside an agent):
```bash
npx github:MDsniper/book-forge           # ← this is what works today
npx github:MDsniper/book-forge --list    # show detected agents, install nothing
npx github:MDsniper/book-forge --all     # install to ALL targets (even undetected)
npx github:MDsniper/book-forge --uninstall
```

(Note: `npx book-forge` without the `github:` prefix would work if book-forge were on the npm registry. It's not yet — only on GitHub. The skill scripts live at `bin/cli.mjs`; you can also run them locally: `node ~/.agents/skills/book-forge/bin/cli.mjs`.)

**Per-agent invocation cheat sheet:**

| Phase | Claude Code / Factory Droid / ZCode | Kimi CLI | OpenCode | OpenClaw / Hermes |
|---|---|---|---|---|
| seed | `/book-forge` | `/skill:book-forge` | "use book-forge to start a book" | "use book-forge to start a book" |
| foundation | `/book-forge foundation` | `/skill:book-forge foundation` | "run book-forge foundation phase" | "run book-forge foundation phase" |
| drafting | `/book-forge drafting` | `/skill:book-forge drafting` | "run book-forge drafting" | "run book-forge drafting" |
| revision | `/book-forge revision` | `/skill:book-forge revision` | "run book-forge revision" | "run book-forge revision" |
| export | `/book-forge export` | `/skill:book-forge export` | "run book-forge export" | "run book-forge export" |
| publish | `/book-forge publish` | `/skill:book-forge publish` | "run book-forge publish" | "run book-forge publish" |

## How it works (in one breath)

A book is **five co-evolving layers + one truth-DB**:

| Layer | Fiction | Nonfiction / Self-help |
|---|---|---|
| `voice.md` | prose style | author voice |
| `world.md` | lore, magic, geography | domain map, terminology |
| `characters.md` | registry, arcs | personas, case figures |
| `outline.md` | beats + foreshadowing ledger | chapter list + thread ledger |
| `chapters/ch_NN.md` | the prose | the prose |
| `canon.md` | hard-facts DB | claims/evidence DB (no fabricated citations) |

Every phase is a **modify → evaluate → keep/discard loop**: generate in persona, evaluate with the immune systems, keep if improved (commit), discard if worse (`git reset --hard HEAD~1`), target the weakest dimension next.

## Book types

`state.json.book_type ∈ {fiction, nonfiction, self-help}` routes foundation and revision:

- **fiction** → world-building + 400+ canon entries + foreshadowing ledger (MICE closure) + 4-persona reader panel
- **nonfiction** → research bible + every claim sourced + argument/thread ledger + fact-check + Skeptic panelist
- **self-help** → as nonfiction, plus Concept→Method→Example→Exercise structure + sensitivity/claimer-of-authority check

Plus a **collaborative mode** (`state.json.collaborative_mode`): at seed time, you can pick **collaborative** (15-question interview + 4 review checkpoints during foundation/revision) or **autonomous** (hands-off, original behavior). See `references/collaborative.md`.

## Dependencies

- **Always required:** `git`, `python3` (you have both).
- **For EPUB/DOCX:** `pandoc` — `brew install pandoc`.
- **For PDF:** a LaTeX engine — `brew install --cask mactex` (full) or `cargo install tectonic` (lightweight).
- **Optional:** `epubcheck` — `brew install epubcheck` (validates EPUB output).
- **For image generation:** at least one of `COMFYUI_URL` (self-hosted), `OPENAI_API_KEY`, `IDEOGRAM_API_KEY`, `GOOGLE_GENAI_API_KEY`, `FAL_KEY`, `STABILITY_API_KEY`, or `REPLICATE_API_TOKEN`.

Export never fails because a tool is missing — it produces what it can and prints install hints.

## Files in this skill

```
book-forge/
├── SKILL.md                     orchestration brain (read this first)
├── README.md                    this file
├── NOTICE                       authorclaw MIT attribution + autonovel credit
├── LICENSE                      MIT
├── package.json                 npm package metadata
├── bin/
│   └── cli.mjs                  npx installer (auto-detects 7 agents)
├── references/                  load on demand (see SKILL.md)
│   ├── methodology.md           5-layer+canon model, the loop, stability trap, anti-inflation
│   ├── foundation.md            phase 1 procedure + scoring + voice discovery + MICE closure
│   ├── drafting.md              phase 2 — chapter-drafting directives, context-window assembly, anti-summarize
│   ├── revision.md              phase 3 — adversarial cut analysis, 4-persona panel, dual-persona review, plateau math
│   ├── quality.md               three immune systems verbatim — slop tiers, judge rubric, reader personas
│   ├── craft.md                 plotting frameworks, foreshadowing ledger, beat math, scene-sequel
│   ├── story-structures.md      the 9 plotting frameworks catalog (Save the Cat, Three-Act, etc.)
│   ├── nonfiction.md            nonfiction & self-help adaptation: research→thesis→evidence→draft→fact-check
│   ├── genres.md                per-genre voice/structure/benchmarks + word-count norms
│   ├── collaborative.md         collaborative mode: interview script + 4 checkpoint protocols
│   ├── images.md                cover & illustration generation — provider setup, brief writing, text-on-image caveats
│   ├── export.md                packaging + front/back matter + KDP readiness
│   ├── publish.md               publish phase: ISBN, copyright page, KDP/Ingram, cover spec, pricing, legal
│   └── launch.md                90-day launch orchestrator + marketing asset bundle
├── assets/
│   ├── templates/               scaffolded into a new book folder at seed time
│   │   ├── state.json, project.yaml, seed.txt, voice.md
│   │   ├── world.md, research-bible.md, characters.md, outline.md
│   │   ├── canon.md, evidence.md, MYSTERY.md, thesis.md
│   │   └── interview-answers.md   (collaborative mode only)
│   ├── banned-words.txt         slop lexicon (Tier 1, Tier 2, fiction, self-help, Tier 3 phrases)
│   ├── ai-tells.txt             regex patterns (sensory cliché, physiological, structural tic, telling verb, filter, nonfiction)
│   └── image-config.example.json  template for any/all of 7 image providers
└── scripts/                     pure stdlib Python 3.9+
    ├── slop_scan.py             mechanical slop scanner (0-10 penalty)
    ├── beat_math.py             structural-beat calculator (fiction + nonfiction)
    ├── assemble.py              chapters/ → manuscript.md, rebuild outline/arc
    ├── export.py                pandoc EPUB/DOCX + LaTeX PDF, graceful-skip on missing tools
    ├── publish.py               copyright page, cover spec, pricing, KDP/Ingram metadata, legal disclaimers, checklist
    └── image.py                 cover/illustration generation via 7 providers, graceful-skip on no key
```

## Per-book structure (created by the seed phase)

```
MyBook/
├── .book-forge/
│   ├── banned-words.txt           project-specific slop overrides (optional)
│   └── ai-tells.txt               project-specific tell overrides (optional)
├── seed.txt
├── interview-answers.md           only if collaborative mode was chosen
├── state.json                     master phase tracker (phase, scores, debts, mode, checkpoints_reached)
├── project.yaml                   metadata (title, author, book_type, targets)
├── voice.md, world.md (or research-bible.md), characters.md
├── outline.md (with ledger), canon.md (or evidence.md)
├── MYSTERY.md (fiction) / thesis.md (nonfiction)
├── chapters/
│   └── ch_01.md ... ch_NN.md
├── briefs/                        revision briefs
├── arc_summary.md                 one-paragraph-per-chapter summary (rebuilt after drafting)
├── manuscript.md                  assembled book (after export)
├── front-matter.md, back-matter.md
├── results.tsv                    audit log (every keep/discard/cycle)
├── publish/                       publish phase output (copyright, cover spec, pricing, metadata, marketing)
└── exports/                       final .epub / .docx / .pdf
```

## Inspiration & credits

book-forge is an original work that draws inspiration from two projects in the AI-book-writing space. All expression in this skill (prompts, lexicons, prose, code) is original to book-forge.

- **[authorclaw](https://github.com/Ckokoski/authorclaw)** (© 2026 Writing Secrets / Beach Blogger LLC, MIT licensed) — portions of this skill adapt ideas from authorclaw, including the write→polish two-step with anti-summarize output rules, the analyze-vs-apply revision discipline, structural beat math, and the no-fabricated-citations hard rule. The MIT license and copyright notice are preserved in [NOTICE](./NOTICE). Per the MIT license, this attribution is provided in derivative work; authorclaw's authors do not endorse this project.

- **[autonovel](https://github.com/NousResearch/autonovel)** (NousResearch) — autonovel's *methodology* (the 5-layer + canon model, the modify-evaluate-keep/discard loop, the use of multiple "immune systems" for quality control, the foreshadowing ledger, the anti-inflation principle) inspired the design of this skill. **No source code or text from autonovel is included.** At the time of this release, autonovel does not carry a license file; we therefore limited our reuse to the ideas and methodology (which are not copyrightable) and wrote all expression from scratch. If autonovel's maintainers add a permissive license, we would welcome the opportunity to credit them more formally.

The book-writing methodology this skill implements (Save the Cat, Story Circle, MICE quotient, Sanderson's Laws, foreshadowing ledgers, scene-sequel structure) predates both projects and is drawn from the open craft literature (Snyder, Harmon, Card, Sanderson, Swain, Weiland, etc.).

## License

MIT.