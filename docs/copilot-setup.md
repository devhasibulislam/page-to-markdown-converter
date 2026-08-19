# Copilot setup

This repo ships a full Copilot customization surface. Everything is checked in
so contributors get the same setup automatically.

## Files

```
.github/
├── copilot-instructions.md          Single always-loaded brief (< 300 lines)
├── instructions/
│   ├── python.instructions.md       applyTo: app/**/*.py
│   ├── typescript.instructions.md   applyTo: extension/**/*.{ts,tsx}
│   ├── templates.instructions.md    applyTo: app/templates/**/*.html
│   └── content.instructions.md      applyTo: app/content/**/*.md
├── prompts/
│   ├── adr.prompt.md                /adr — new decision record
│   ├── blog.prompt.md               /blog — new blog post scaffold
│   ├── route.prompt.md              /route — FastAPI route + test
│   └── extract-test.prompt.md       /extract-test — extraction fixture
└── chatmodes/
    ├── plan.chatmode.md             Plan mode (research anywhere, edit nothing)
    └── review.chatmode.md           Review mode (over-engineering, reusability, standards)
.vscode/
├── mcp.json                         GitHub + Playwright MCP
├── settings.json                    Auto-approve list, agent settings
└── extensions.json                  Recommended extensions
skills/
└── extraction-quality/SKILL.md      Project-local skill: fixture quality checklist
hooks/                               Enforced by .pre-commit-config.yaml
.pre-commit-config.yaml              ruff + mypy + pytest -x on commit
```

## Why Copilot-only

Decision recorded in [`decisions/0007-copilot-only-no-cross-agent-mirrors.md`](decisions/0007-copilot-only-no-cross-agent-mirrors.md).

Short version: this is a Copilot-first project. Maintaining parallel
`AGENTS.md` and `.claude/CLAUDE.md` files adds work with no benefit for our
workflow. If we adopt another agent later, `.github/copilot-instructions.md`
is easy to mirror.

## How each layer earns its place

### `.github/copilot-instructions.md` — the brief

Auto-loaded on every chat. Contains the golden rules, the stack, run commands,
and pointers to everything else. Kept under 300 lines to stay in context.

### `.github/instructions/*.instructions.md` — scoped rules

Each file has `applyTo:` frontmatter. Loaded only when the agent touches
matching files. Keeps context lean: editing a Python file doesn't drag in the
TypeScript rules.

### `.github/prompts/*.prompt.md` — slash commands

Reusable scaffolds:

- `/adr <title>` — numbers the next ADR automatically
- `/blog <title>` — correct frontmatter every time
- `/route <path>` — FastAPI route + test + registration
- `/extract-test <url>` — fetch, snapshot, add fixture

### `.github/chatmodes/*.chatmode.md` — modes

**Plan mode** — can research anywhere (web fetch, SSH into a VPS via terminal,
curl, docker inspection), cannot edit files. Terminal is off the auto-approve
list in `settings.json`, so every shell command surfaces a confirm dialog.
System prompt forbids mutating commands.

**Review mode** — read-only. Enforces:

1. Over-engineering (loads ponytail-review skill)
2. Reusability / no redundancy (uses `vscode_listCodeUsages` on every non-trivial function, greps for duplicate logic patterns)
3. Industry standards (PEP 8, type hints, Pydantic v2, thin routes, strict TS, one-line comments only when code can't show it, naming, error handling, test discipline)
4. Layout (files over 300 lines mixing concerns, dumping-ground utils)

Output: one line per finding, grouped by delete / merge / rewrite / nit. No prose padding.

### `.vscode/mcp.json` — MCP servers

- **GitHub MCP** — issues, PRs, releases
- **Playwright MCP** — extension E2E, install-video recording

Not wired: MongoDB / Atlas MCPs (no database), filesystem MCP (Copilot has file tools already).

### `skills/extraction-quality/SKILL.md`

Project-local skill listing the fixture-quality checklist. Loaded when adding
a new extraction test.

### `.pre-commit-config.yaml` (hooks)

Enforces the rules mechanically: `ruff check --fix`, `ruff format`, `mypy app/`,
`pytest -x --ff` on every commit. A bad commit fails locally before it can
ship.

### `.vscode/settings.json` — auto-approve

Conservative allowlist: read-only tools auto-run, `run_in_terminal` requires
confirmation. Prevents accidental destructive actions.

## Extending this setup

Any new agent-facing convention must be listed in
`.github/copilot-instructions.md`. If it isn't referenced there, Copilot won't
know it exists.

New instruction file? Add `.github/instructions/<name>.instructions.md` with an
`applyTo:` glob, then reference it in `copilot-instructions.md`.

New slash command? Add `.github/prompts/<name>.prompt.md`, reference it.

New chat mode? Add `.github/chatmodes/<name>.chatmode.md`, document what it can
and can't do, and reference it.
