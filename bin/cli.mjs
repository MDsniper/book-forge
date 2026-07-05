#!/usr/bin/env node
// book-forge — installer & sync for the book-writing Agent Skill.
//
// Detects installed AI coding agents and installs (or syncs) book-forge into
// each agent's skills directory. Idempotent.
//
// Usage:
//   npx book-forge                 # auto-detect + install to all detected
//   npx book-forge --list          # show detection, install nothing
//   npx book-forge --all           # install to ALL targets, even undetected
//   npx book-forge --target claude # install to one named target only
//   npx book-forge claude          # (same as --target claude)
//   npx book-forge --uninstall     # remove book-forge from all targets
//   npx book-forge -h | --help
//
// Pure stdlib — no runtime dependencies. Node >= 18.

import { spawnSync } from "node:child_process";
import {
  cpSync, existsSync, mkdirSync, realpathSync, rmSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { homedir, platform } from "node:os";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
// Skill root = parent of bin/. The bundled skill files live there.
const SKILL_ROOT = dirname(__dirname);
const SKILL_NAME = "book-forge";

const HOME = homedir();

// Each target: where to install + how to detect if the agent is present.
const TARGETS = [
  { name: "zcode", label: "ZCode",
    path: join(HOME, ".agents", "skills", SKILL_NAME),
    detect: () => existsSync(join(HOME, ".zcode")) || existsSync(join(HOME, ".agents", "skills")) },
  { name: "claude", label: "Claude Code",
    path: join(HOME, ".claude", "skills", SKILL_NAME),
    detect: () => existsSync(join(HOME, ".claude")) || which("claude") },
  { name: "factory", label: "Factory Droid",
    path: join(HOME, ".factory", "skills", SKILL_NAME),
    detect: () => existsSync(join(HOME, ".factory")) || which("droid") || which("factory") },
  { name: "opencode", label: "OpenCode",
    path: join(HOME, ".config", "opencode", "skills", SKILL_NAME),
    detect: () => existsSync(join(HOME, ".config", "opencode")) || which("opencode") },
  { name: "kimi", label: "Kimi CLI",
    path: join(HOME, ".kimi", "skills", SKILL_NAME),
    detect: () => existsSync(join(HOME, ".kimi")) || which("kimi") },
  { name: "openclaw", label: "OpenClaw",
    path: join(HOME, ".openclaw", "skills", SKILL_NAME),
    detect: () => existsSync(join(HOME, ".openclaw")) || which("openclaw") },
  { name: "hermes", label: "Hermes Agent",
    path: join(HOME, ".hermes", "skills", "writing", SKILL_NAME),
    detect: () => existsSync(join(HOME, ".hermes", "skills")) || which("hermes") },
];

const isTTY = process.stdout.isTTY;
const c = {
  green: (s) => (isTTY ? `\x1b[32m${s}\x1b[0m` : s),
  red: (s) => (isTTY ? `\x1b[31m${s}\x1b[0m` : s),
  cyan: (s) => (isTTY ? `\x1b[36m${s}\x1b[0m` : s),
  dim: (s) => (isTTY ? `\x1b[2m${s}\x1b[0m` : s),
  bold: (s) => (isTTY ? `\x1b[1m${s}\x1b[0m` : s),
};

function which(bin) {
  try {
    const r = spawnSync(platform() === "win32" ? "where" : "which",
                        [bin], { stdio: "ignore" });
    return r.status === 0;
  } catch {
    return false;
  }
}

function parseArgs(argv) {
  const out = { list: false, all: false, uninstall: false, target: null, help: false };
  const args = argv.slice(2);
  for (let i = 0; i < args.length; i++) {
    const a = args[i];
    if (a === "-h" || a === "--help") out.help = true;
    else if (a === "--list") out.list = true;
    else if (a === "--all") out.all = true;
    else if (a === "--uninstall") out.uninstall = true;
    else if (a === "--sync") { /* default behavior, alias */ }
    else if (a === "--target") out.target = args[++i];
    else if (a.startsWith("--target=")) out.target = a.slice("--target=".length);
    else if (!a.startsWith("-")) out.target = a;
  }
  return out;
}

const HELP = `book-forge — install the autonomous book-writing skill into your AI agents.

Usage:
  npx book-forge                Auto-detect installed agents and install/sync.
  npx book-forge --list         Show detection results; install nothing.
  npx book-forge --all          Install to ALL targets, even undetected ones.
  npx book-forge --target <id>  Install to one named target.
  npx book-forge claude         (same as --target claude)
  npx book-forge --uninstall    Remove book-forge from every target.
  npx book-forge -h | --help    Show this help.

Targets: ${TARGETS.map((t) => t.name).join(", ")}

After install, invoke from any agent: most use \`/book-forge\`; OpenCode,
OpenClaw, and Hermes auto-load by description.

To start a book:
  mkdir ~/Documents/MyBook && cd ~/Documents/MyBook
  /book-forge
`;

// Install (or re-sync) the skill to one target. SAFETY: the destination is
// never an ancestor of the source (would be a self-wipe), and the filter only
// excludes node_modules / .git (NOT bin/ — bin/ is part of the skill).
// Safety check: refuse to install into (or remove) a path that resolves
// to the same location as the source. Uses realpathSync so symlinks
// (some agents, e.g. OpenClaw, use symlinks under ~/.openclaw/skills/) are
// compared at their actual target, not their textual path. This is the
// bug that previously allowed the canonical's .git to be wiped by an
// installer run from a different working directory.
function _pathsOverlap(a, b) {
  if (!a || !b) return false;
  let ra, rb;
  try { ra = realpathSync(a); } catch { ra = a; }
  try { rb = realpathSync(b); } catch { rb = b; }
  // Normalize trailing slashes
  ra = ra.replace(/\/+$/, "");
  rb = rb.replace(/\/+$/, "");
  if (ra === rb) return true;
  return ra.startsWith(rb + "/") || rb.startsWith(ra + "/");
}

function installTo(target) {
  if (!existsSync(join(SKILL_ROOT, "SKILL.md"))) {
    console.error(c.red(`✗ source SKILL.md not found at ${SKILL_ROOT}`));
    return false;
  }
  // Resolve real paths (handles symlinks — see _pathsOverlap comment).
  if (_pathsOverlap(SKILL_ROOT, target.path)) {
    console.error(c.red(`✗ refusing to install into a path that overlaps the source (${target.path})`));
    return false;
  }
  mkdirSync(dirname(target.path), { recursive: true });
  if (existsSync(target.path)) rmSync(target.path, { recursive: true, force: true });
  cpSync(SKILL_ROOT, target.path, {
    recursive: true,
    filter: (src) => {
      const base = src.split("/").pop();
      return base !== "node_modules" && base !== ".git";
    },
  });
  return true;
}

function uninstallFrom(target) {
  if (!existsSync(target.path)) return "absent";
  // Same overlap safety.
  if (_pathsOverlap(SKILL_ROOT, target.path)) {
    console.error(c.red(`✗ refusing to remove source path (${target.path})`));
    return "blocked";
  }
  rmSync(target.path, { recursive: true, force: true });
  return "removed";
}

// (dirname is imported at the top of this file from node:path)


function main() {
  const args = parseArgs(process.argv);
  if (args.help) {
    process.stdout.write(HELP);
    return 0;
  }

  console.log(c.bold(c.cyan("\nbook-forge")) +
              c.dim(" — autonomous book-writing skill installer\n"));
  console.log(c.dim(`source: ${SKILL_ROOT}`));

  const detected = TARGETS.filter((t) => t.detect());
  console.log(c.dim(`detected ${detected.length}/${TARGETS.length} agents on this machine\n`));

  if (args.list) {
    console.log("Detection results:");
    for (const t of TARGETS) {
      const mark = t.detect() ? c.green("✓") : c.dim("·");
      console.log(`  ${mark} ${t.name.padEnd(10)} ${t.label.padEnd(16)} ${c.dim(t.path)}`);
    }
    console.log(`\nRun ${c.cyan("npx book-forge")} (no flags) to install.`);
    return 0;
  }

  if (args.uninstall) {
    console.log("Uninstalling book-forge from all targets:");
    let any = false;
    for (const t of TARGETS) {
      const r = uninstallFrom(t);
      if (r === "removed") {
        console.log(`  ${c.green("✓")} removed from ${t.name.padEnd(10)} ${c.dim(t.path)}`);
        any = true;
      }
    }
    if (!any) console.log(c.dim("  (nothing to remove — book-forge wasn't installed anywhere)"));
    return 0;
  }

  let targets;
  if (args.target) {
    const t = TARGETS.find((x) => x.name === args.target);
    if (!t) {
      console.error(c.red(`✗ unknown target "${args.target}". Valid: ${TARGETS.map((x) => x.name).join(", ")}`));
      return 2;
    }
    targets = [t];
  } else if (args.all) {
    targets = TARGETS;
  } else {
    targets = detected;
    if (targets.length === 0) {
      console.error(c.red("\n✗ no supported agents detected."));
      console.error(c.dim("  Run `npx book-forge --all` to install everywhere regardless of detection."));
      return 1;
    }
  }

  console.log(`Installing to ${targets.length} target${targets.length === 1 ? "" : "s"}:\n`);
  let ok = 0;
  for (const t of targets) {
    const success = installTo(t);
    if (success) {
      console.log(`  ${c.green("✓")} ${t.name.padEnd(10)} ${t.label.padEnd(16)} ${c.dim(t.path)}`);
      ok++;
    }
  }
  console.log(`\n${c.green("Done.")} ${ok}/${targets.length} target${targets.length === 1 ? "" : "s"} installed.`);
  console.log(`\nNext: ${c.cyan("mkdir ~/Documents/MyBook && cd ~/Documents/MyBook")}`);
  console.log(`      then in your agent: ${c.cyan("/book-forge")}`);
  console.log(c.dim("\nRe-run any time to re-sync after updates.\n"));
  return 0;
}

try {
  process.exitCode = main();
} catch (err) {
  console.error(c.red(`\n✗ ${err.message}`));
  if (process.env.DEBUG) console.error(err.stack);
  process.exitCode = 1;
}
